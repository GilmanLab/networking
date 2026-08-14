---
title: GilmanLab Networking
slug: /
description: Architecture and operating documentation for the GilmanLab core network.
---

# GilmanLab Networking

This repository defines the GilmanLab core network. VyOS handles routing and
firewall policy. MikroTik handles switching and VLAN transport.

Lab v2 is in the design phase. Proposed topology, addressing, traffic policy,
and operations are not current architecture until they are implemented and
verified.

## Current documentation

- [Lab v2 core network design](designs/drafts/lab-v2-core-network.md) defines
  the design scope, unresolved choices, and acceptance evidence.
- [ADR-0001: Use VyOS for Layer 3 and MikroTik for Layer 2](decisions/0001-use-vyos-for-layer-3-and-mikrotik-for-layer-2.md)
  assigns routing and switching responsibilities.
- [Hardware](reference/hardware.md) records known equipment facts and identifies
  facts that still require physical verification.

Compute platforms, workload networking, and application delivery are outside
the current design scope.
