# Example files

These are sanitized reconstructions, not downloads from the live host. Replace placeholders only in private copies. No scripts in this directory were run against the actual VPN host or DNS zone while preparing this package.

| File | Use and limitation |
| --- | --- |
| cloudflare-ddns.example.conf | Root-only shell configuration; fill locally |
| cloudflare-ddns.example.sh | Updates exactly one existing DNS-only A record; dependencies and safeguards are in the script |
| cloudflare-ddns.service | Oneshot systemd service; reconstructed sandbox settings |
| cloudflare-ddns.timer | Reconstructed timer; five-minute cadence is an example |
| host-firewall.example.sh | Host INPUT filter only; does not flush forwarding/NAT chains |
| host-firewall.service | Reconstructed boot unit |
| docker-compose.example.yml | Topology illustration; deliberately not launchable |

The DDNS token is scoped to the zone, while the script selects a single hostname. The example refuses multiple matches and will not create a missing record, enable the Cloudflare proxy, change another hostname, or touch AAAA records. It patches only A-record content. Choose and assess the public IPv4 lookup provider separately.

The firewall example needs a console-based review. It accepts established connections and necessary ICMP/ICMPv6, allows IPv4 SSH from the trusted subnet, and exposes intended host web/STUN ports. It provides no guarantee about forwarded Docker or NetBird traffic. Check the upstream gateway and both address families.

The Compose file leaves out generated settings, credentials, and routing labels. Use the official installer and preserve its private output. A full `netbird-config.example.yaml` is intentionally omitted because the actual server configuration was not supplied for inspection; guessing authentication schema would be misleading.

Review the walkthrough before applying anything. Local validation covered shell syntax, config/unit/YAML structure, and mocked script behavior. Integration and recovery tests belong on an isolated replica before production changes.
