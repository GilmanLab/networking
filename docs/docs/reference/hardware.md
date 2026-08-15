---
title: Hardware
description: Core network devices, connections, and assigned roles.
---

# Hardware

## Core devices

| Component | Platform | Role |
| --- | --- | --- |
| Lab gateway | Minisforum VP6630 running VyOS | Routes lab networks, enforces firewall policy, and performs source NAT |
| Core switch | MikroTik `CRS309-1G-8S+IN` | Carries lab VLANs and connects lab devices at Layer 2 |
| Management/OOB switch | TRENDnet `TEG-3102WS` | Connects both non-SFP NICs from each MS-02 for management/OOB traffic |

## External dependency

| Component | Platform | Role |
| --- | --- | --- |
| Home router | MikroTik CCR2004 | Routes the home network, provides internet access, and terminates the upstream side of the routed lab transit |

## Connections

| Endpoints | Connection |
| --- | --- |
| CCR2004 to VP6630 | Routed lab transit |
| VP6630 to CRS309-1G-8S+IN | 802.1Q trunk for lab VLANs |
| VP6630 to TEG-3102WS | Direct management/OOB uplink |
| TEG-3102WS to each MS-02 | Two non-SFP NICs carrying management/OOB traffic |

See the [Lab v2 core network design](../designs/drafts/lab-v2-core-network.md)
for the topology and device boundaries.
