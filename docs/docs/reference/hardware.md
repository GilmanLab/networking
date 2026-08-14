---
title: Hardware
description: Core network devices and their assigned roles.
---

# Hardware

## Core devices

| Component | Platform | Role |
| --- | --- | --- |
| Lab gateway | Minisforum VP6630 running VyOS | Routes lab networks, enforces firewall policy, and performs source NAT |
| Lab switch | MikroTik switch | Carries VLANs and connects lab devices at Layer 2 |

## External dependency

| Component | Platform | Role |
| --- | --- | --- |
| Home router | MikroTik CCR2004 | Routes the home network, provides internet access, and terminates the upstream side of the routed lab transit |

See the [Lab v2 core network design](../designs/drafts/lab-v2-core-network.md)
for the topology and device boundaries.
