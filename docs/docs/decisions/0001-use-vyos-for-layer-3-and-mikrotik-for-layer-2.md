---
status: accepted
date: 2026-08-14
---

# ADR-0001: Use VyOS for Layer 3 and MikroTik for Layer 2

## Context and Problem Statement

The Lab v2 core network needs explicit ownership for switching, routing, and
traffic policy. The selected hardware includes a VyOS gateway and a MikroTik
switch. Which device should own each network function?

## Decision Drivers

- Keep routed gateways and firewall policy on one device.
- Keep the switch configuration focused on VLAN transport and physical links.
- Make the enforcement point for traffic between routed lab segments explicit.
- Use the selected VyOS and MikroTik hardware.

## Considered Options

- Use VyOS for Layer 3 and MikroTik for Layer 2.
- Use MikroTik for Layer 2 and Layer 3, with VyOS at the external edge.
- Use one flat Layer 2 lab network, with VyOS as its external gateway.

## Decision Outcome

Use VyOS for routed lab gateways, route selection, firewall policy, and NAT.
Use MikroTik for Layer 2 switching, VLAN transport, and physical link
aggregation.

DHCP and DNS ownership are not part of this decision. The
[Lab v2 core network design](../designs/drafts/lab-v2-core-network.md) will
assign those functions.

### Consequences

- Good, because routed traffic has one policy-enforcement point.
- Good, because each device has a distinct configuration boundary.
- Bad, because traffic between routed lab segments depends on VyOS.
- Bad, because routed segments carried through the switch depend on the trunk
  between VyOS and MikroTik.

### Confirmation

The implementation conforms to this decision when:

- VyOS owns the gateway address for each routed lab segment.
- VyOS contains the firewall and NAT policy for routed lab traffic.
- MikroTik does not route traffic between lab segments.
- MikroTik configuration defines VLAN membership, trunks, access ports, and
  physical link aggregation.

A management address on the MikroTik switch does not violate this decision.

## Pros and Cons of the Options

### VyOS Layer 3 and MikroTik Layer 2

- Good, because routing and firewall policy use the same configuration
  boundary.
- Good, because the switch remains independent of higher-level traffic policy.
- Bad, because VyOS is on the forwarding path for all routed lab traffic.

### MikroTik Layer 2 and Layer 3

- Good, because the switch can route traffic without sending it through the
  VyOS trunk.
- Bad, because firewall and routing ownership would be split between devices.
- Bad, because Lab v2 would need policy coordination between MikroTik and VyOS.

### Flat Layer 2 lab network

- Good, because it requires fewer routed interfaces and policies.
- Bad, because it cannot enforce boundaries between lab network functions.
- Bad, because broadcasts and Layer 2 failures share one domain.

## More Information

The Lab v1
[VyOS gateway configuration](https://github.com/GilmanLab/lab/blob/master/infrastructure/network/vyos/configs/gateway.conf)
used the same router-and-switch responsibility split. Lab v2 will verify the
hardware mapping and redesign the detailed configuration instead of treating
that file as current configuration.
