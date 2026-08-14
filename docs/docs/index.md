---
title: GilmanLab Networking
slug: /
description: Architecture and operating documentation for the GilmanLab core network.
---

# GilmanLab Networking

This repository defines the GilmanLab core network. VyOS handles routing,
firewall policy, and NAT. MikroTik handles switching and VLAN transport.

## Documents

- [Lab v2 core network design](designs/drafts/lab-v2-core-network.md) defines
  the core topology, device boundaries, configuration requirements, and
  verification criteria.
- [ADR-0001: Use VyOS for Layer 3 and MikroTik for Layer 2](decisions/0001-use-vyos-for-layer-3-and-mikrotik-for-layer-2.md)
  assigns routing and switching responsibilities.
- [Hardware](reference/hardware.md) identifies the core network devices and
  their roles.

Compute platforms, workload networking, and application delivery are outside
the core network documentation.
