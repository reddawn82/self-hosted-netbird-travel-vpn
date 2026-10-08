#!/usr/bin/env bash
# EXAMPLE ONLY -- reconstructed host INPUT filter, not a forwarding firewall.
# Review and populate at a local console. Do not flush Docker/NetBird chains.
# Reapplying rebuilds this chain; briefly interrupted new inbound traffic is possible.
set -euo pipefail
trusted_lan='<HOME_LAN_CIDR>'
chain=RDN-HOST-IN
[[ $EUID -eq 0 ]] || { echo 'Run as root' >&2; exit 1; }
python3 - "$trusted_lan" <<'PY'
import ipaddress, sys
try:
    network = ipaddress.ip_network(sys.argv[1], strict=True)
    assert network.version == 4 and network.is_private
except (ValueError, AssertionError):
    raise SystemExit('Replace HOME_LAN_CIDR with the trusted private IPv4 subnet')
PY
for command in iptables ip6tables; do
  command -v "$command" >/dev/null
  "$command" -w -N "$chain" 2>/dev/null || "$command" -w -S "$chain" >/dev/null
  "$command" -w -F "$chain"
  "$command" -w -A "$chain" -i lo -j ACCEPT
  "$command" -w -A "$chain" -m conntrack \
    --ctstate ESTABLISHED,RELATED -j ACCEPT
  if [[ $command == iptables ]]; then
    "$command" -w -A "$chain" -p icmp -j ACCEPT
    "$command" -w -A "$chain" -p tcp -s "$trusted_lan" --dport 22 -j ACCEPT
  else
    # Neighbor discovery and path MTU rely on ICMPv6.
    "$command" -w -A "$chain" -p ipv6-icmp -j ACCEPT
    # Accommodate DHCPv6 on the host; review interface scope for your network.
    "$command" -w -A "$chain" -p udp --sport 547 --dport 546 -j ACCEPT
  fi
  "$command" -w -A "$chain" -p tcp -m multiport --dports 80,443 -j ACCEPT
  "$command" -w -A "$chain" -p udp --dport 3478 -j ACCEPT
  "$command" -w -A "$chain" -j DROP
  # A single first-position jump controls unsolicited host input.
  while "$command" -w -C INPUT -j "$chain" 2>/dev/null; do
    "$command" -w -D INPUT -j "$chain"
  done
  "$command" -w -I INPUT 1 -j "$chain"
done
# Intentionally do not change FORWARD, NAT, DOCKER-USER or NetBird rules.
