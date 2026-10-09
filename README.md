# Self Hosted NetBird Travel VPN

This project documents a self-hosted NetBird environment for remote home-network access and authorized Internet traffic through a home connection. Docker and Traefik host the control plane, Cloudflare maintains the VPN hostname through DDNS, and a Linux host client acts as the LAN routing peer and Internet exit node.

## Status

Phase 1 server-side implementation is complete. A cellular phone reached a home LAN device and was observed using the home IPv4 and IPv6 exit. Services and the host peer recovered automatically after reboot. DNS functionality worked, but its routing path was inconclusive. A full restore rehearsal and complete post-reboot route retest are not recorded.

Phase 2 Beryl AX travel-router deployment is pending hardware. Confirm the exact purchased model before selecting an OpenWrt package.

## Architecture

![Control plane and home exit](assets/architecture/architecture.svg)

Control-plane web requests reach Traefik over HTTPS. Peer traffic reaches the Linux routing peer over the encrypted NetBird tunnel; it does not use the dashboard as an Internet gateway. Direct peer connectivity is preferred, with relay transport available when needed.

## Read the walkthrough

[Full walkthrough](docs/self-hosted-netbird-travel-vpn.md) covers laptop power management, key-based SSH, DNS-only records, record-specific DDNS behavior, gateway mappings, host filtering, installation, NAT loopback troubleshooting, peer enrollment, LAN and exit routing, IPv6/DNS testing, Docker exposure, backups, and recovery.

The walkthrough includes complete custom DDNS and firewall files, their paths and permissions, and timer activation steps. Installer-generated files are identified with creation and verification guidance; excerpts are clearly labeled.

## Technologies

Kali Linux, Docker Compose, NetBird server and Linux client, Traefik, Let's Encrypt, Cloudflare DNS/API, systemd, OpenSSH, iptables/ip6tables, and an AT&T residential gateway.

## Security model

SSH is not publicly forwarded. Peer enrollment uses one-off or short-lived credentials, and exit authorization is explicit. Docker publishes only TCP/80, TCP/443 and UDP/3478. Public examples contain placeholders; private configurations and backups stay outside the repository. Host INPUT rules do not independently protect Docker-published ports. A default route can reach other networks accessible to the exit host; limited LAN isolation has not been proven.

Local MFA was deferred because it appeared as beta in the deployed interface. Posture checks and managed DNS were also deferred. See the walkthrough for historical decisions and optional hardening.

## Configuration examples

[Configuration examples](examples/README.md) accompany the walkthrough, including DDNS automation, systemd units, and host firewall rules. Review the example guide for each file's purpose and limitations.

The Compose example illustrates the architecture and deliberately cannot launch. Use the official NetBird installer for a deployment and follow the walkthrough's configuration and verification steps.
