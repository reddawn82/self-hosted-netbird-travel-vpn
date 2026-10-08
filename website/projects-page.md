# Self Hosted Travel VPN

This project uses a repurposed Linux laptop to provide remote access to a home network and route authorized travel devices through the home Internet connection.

The server hosts NetBird with Docker and Traefik, uses Let's Encrypt for HTTPS, and maintains its VPN hostname with Cloudflare DDNS. A NetBird client on the same host provides LAN routing and Internet exit. Administration uses key-based SSH without public port forwarding.

The main deployment challenges were keeping the laptop awake with its lid closed, resolving a residential gateway's NAT loopback failure, checking Docker and IPv6 exposure, and preserving configuration and persistent state for recovery.

The server phase is complete. A phone on cellular reached a home LAN device and used the home IPv4 and IPv6 exit. Services and the routing peer returned after reboot. DNS worked, although its routing path was not conclusively validated. The Beryl travel-router phase is pending hardware.

## Explore the project

- Read the full Knowledge Base walkthrough: `<KNOWLEDGE_BASE_ARTICLE_URL>`
- View the documentation and sanitized examples on GitHub: `<GITHUB_REPOSITORY_URL>`

Replace these link placeholders only after the reviewed destinations exist. This draft has not been published.
