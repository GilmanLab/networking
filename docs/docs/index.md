---
title: GilmanLab Networking
slug: /
description: Architecture and operating documentation for the GilmanLab core network.
---

# GilmanLab Networking

This repository defines the GilmanLab core network. VyOS handles routing,
firewall policy, and NAT. A MikroTik CRS309-1G-8S+IN handles core switching and
VLAN transport. A TRENDnet TEG-3102WS handles MS-02 management/OOB switching.

## Documents

- [Lab v2 core network design](designs/drafts/lab-v2-core-network.md) defines
  the core topology, device boundaries, configuration requirements, and
  verification criteria.
- [ADR-0001: Use VyOS for Layer 3 and Dedicated Switches for Layer 2](decisions/0001-use-vyos-for-layer-3-and-switches-for-layer-2.md)
  assigns routing and switching responsibilities.
- [Hardware](reference/hardware.md) identifies the core network devices and
  their roles.
- [Physical connections](reference/physical-connections.md) records every
  installed cable and its endpoint ports.

Compute platforms, workload networking, and application delivery are outside
the core network documentation.
