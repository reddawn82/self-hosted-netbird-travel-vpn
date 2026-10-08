#!/usr/bin/env bash
# EXAMPLE ONLY -- reconstructed; not exported from the live server.
# Updates only ONE existing DNS-only A record for VPN_DOMAIN.
# Dependencies: bash, curl, jq, python3, flock, stat, mktemp.
set -euo pipefail
umask 077
config=/etc/cloudflare-ddns.conf
[[ $EUID -eq 0 ]] || { echo 'Run as root' >&2; exit 1; }
[[ -f $config && ! -L $config ]] || { echo 'Missing regular config' >&2; exit 1; }
[[ $(stat -c '%u:%g:%a' "$config") == '0:0:600' ]] || {
  echo 'Config must be root:root mode 600' >&2; exit 1;
}
# Only source a reviewed root-owned configuration.
# shellcheck source=/dev/null
source "$config"
for value in "${CLOUDFLARE_API_TOKEN:-}" "${CLOUDFLARE_ZONE_ID:-}" \
  "${VPN_DOMAIN:-}" "${PUBLIC_IPV4_URL:-}"; do
  [[ -n $value && $value != *'<'* && $value != *'>'* ]] || {
    echo 'Configuration has missing values or placeholders' >&2; exit 1;
  }
done
[[ $CLOUDFLARE_ZONE_ID =~ ^[a-fA-F0-9]{32}$ ]] || {
  echo 'Invalid zone identifier' >&2; exit 1;
}
# Reject characters that could become curl configuration directives.
[[ $CLOUDFLARE_API_TOKEN =~ ^[a-zA-Z0-9_-]+$ ]] || {
  echo 'Invalid token format' >&2; exit 1;
}
[[ $VPN_DOMAIN =~ ^[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?$ \
  && $VPN_DOMAIN == *.* ]] || { echo 'Invalid hostname' >&2; exit 1; }
exec 9>/run/lock/cloudflare-ddns.lock
flock -n 9 || exit 0
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
# Keep the API token out of the curl process argument list.
printf 'header = "Authorization: Bearer %s"\n' \
  "$CLOUDFLARE_API_TOKEN" > "$work/auth"
public_ipv4=$(curl -4 -fsS --connect-timeout 10 --max-time 30 \
  --proto '=https' "$PUBLIC_IPV4_URL")
python3 - "$public_ipv4" <<'PY'
import ipaddress, sys
try:
    address = ipaddress.ip_address(sys.argv[1])
    assert address.version == 4 and address.is_global
except (ValueError, AssertionError):
    raise SystemExit('Address provider did not return a global IPv4')
PY
api="https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records"
curl -fsS --connect-timeout 10 --max-time 30 --proto '=https' \
  --config "$work/auth" --get "$api" \
  --data-urlencode 'type=A' --data-urlencode "name=$VPN_DOMAIN" \
  --data-urlencode 'per_page=100' > "$work/records"
jq -e '.success == true and (.result | length) == 1' \
  "$work/records" >/dev/null || {
  echo 'API failed or record selection was ambiguous' >&2; exit 1;
}
jq -e --arg name "${VPN_DOMAIN,,}" \
  '.result[0] | .type == "A" and (.name | ascii_downcase) == $name
    and .proxied == false' "$work/records" >/dev/null || {
  echo 'Selected record must match the hostname and be DNS-only' >&2; exit 1;
}
record_id=$(jq -r '.result[0].id' "$work/records")
[[ $record_id =~ ^[a-fA-F0-9]{32}$ ]] || {
  echo 'Invalid record identifier' >&2; exit 1;
}
current_ipv4=$(jq -r '.result[0].content' "$work/records")
if [[ $current_ipv4 == "$public_ipv4" ]]; then
  echo 'A record unchanged'
  exit 0
fi
jq -n --arg address "$public_ipv4" '{content:$address}' > "$work/payload"
# PATCH content only: leave TTL, name, comments, other records and AAAA untouched.
curl -fsS --connect-timeout 10 --max-time 30 --proto '=https' \
  --config "$work/auth" -X PATCH "$api/$record_id" \
  -H 'Content-Type: application/json' --data-binary "@$work/payload" \
  > "$work/update"
jq -e --arg address "$public_ipv4" --arg name "${VPN_DOMAIN,,}" \
  '.success == true and .result.content == $address and .result.type == "A"
    and (.result.name | ascii_downcase) == $name and .result.proxied == false' \
  "$work/update" >/dev/null || { echo 'Update validation failed' >&2; exit 1; }
echo 'A record updated'
