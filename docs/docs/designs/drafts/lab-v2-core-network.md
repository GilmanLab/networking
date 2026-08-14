---
title: Lab v2 core network
status: draft
authors:
  - GilmanLab
created: 2026-08-14
updated: 2026-08-14
related-decisions:
  - ADR-0001
---

# Lab v2 core network

## Summary

The core network uses a Minisforum VP6630 running VyOS for Layer 3 routing,
firewall policy, and NAT. A MikroTik switch handles Layer 2 switching and VLAN
transport. A MikroTik CCR2004 connects the lab to the home network and the
internet.

This design defines device responsibilities, logical topology, configuration
requirements, failure boundaries, and verification criteria. Address
allocation, VLAN allocation, physical port assignment, and network-service
ownership are outside this document.

## Goals

- Keep routing and traffic policy on VyOS.
- Keep VLAN transport and physical switching on MikroTik.
- Route home-to-lab traffic without source NAT.
- Apply source NAT to lab-to-internet traffic on VyOS.
- Store network-device configuration in version control.
- Validate behavior before saving a deployed configuration.
- Preserve a recovery path that does not depend on the primary network path.

## Non-goals

- Address and VLAN allocation
- Physical port and cable assignment
- DHCP, DNS, or time-service ownership
- Compute-platform network configuration
- Workload network overlays
- Application ingress or service advertisement
- Application DNS records
- Service-to-service traffic policy
- Storage protocol design

## Logical Topology

```mermaid
flowchart LR
    HOME[Home network] --> CCR[CCR2004]
    CCR -->|Routed transit| VYOS[VP6630 running VyOS]
    VYOS -->|802.1Q trunk| SWITCH[MikroTik switch]
    SWITCH --> SEGMENTS[Lab network segments]
```

The CCR2004 routes traffic between the home network and the VyOS transit
interface. VyOS routes lab prefixes, applies firewall policy, and performs
source NAT for internet egress. The MikroTik switch carries VLANs between VyOS
and connected lab devices.

## Device Responsibilities

| Device | Responsibilities |
| --- | --- |
| MikroTik CCR2004 | Home-network routing, internet access, and the upstream side of the routed lab transit |
| Minisforum VP6630 running VyOS | Lab gateways, route selection, firewall policy, source NAT, and the downstream side of the routed transit |
| MikroTik switch | VLAN transport, access ports, trunks, and physical link aggregation |

[ADR-0001](../../decisions/0001-use-vyos-for-layer-3-and-mikrotik-for-layer-2.md)
defines the Layer 2 and Layer 3 boundary.

## Routing and NAT

The routing design has these invariants:

- The CCR2004 has routes for lab prefixes through the VyOS transit address.
- VyOS uses the CCR2004 transit address as its default route.
- VyOS owns the gateway address for every routed lab segment.
- MikroTik does not route between lab segments.
- Home-to-lab traffic retains its original source address.
- VyOS applies source NAT to lab-to-internet traffic.
- Firewall rules distinguish new connections from established reply traffic.

## Traffic Policy

VyOS enforces policy for:

- Home network to lab segments
- Lab segments to the home network
- Lab segments to the internet
- Traffic between routed lab segments
- Traffic addressed to VyOS
- Management traffic addressed to network devices

Each firewall rule identifies the source, destination, protocol, destination
port, connection direction, and owner. Rules permit required flows explicitly.
Stateful rules permit established reply traffic without permitting a new flow in
the reverse direction.

## Configuration Requirements

VyOS and MikroTik each have one version-controlled configuration source. The
deployment process:

1. Renders the effective configuration.
2. Validates syntax and policy before deployment.
3. Shows the effective change for operator review.
4. Applies the change without saving it as the startup configuration.
5. Verifies required connectivity and policy behavior.
6. Saves the configuration only after verification succeeds.
7. Restores the previous configuration when verification fails.

Drift detection compares each running configuration with its repository source.

## Management and Recovery

Firewall policy limits routine management access to approved source networks.

Each device has a recovery path that remains available when its production
configuration or primary network link fails. Recovery credentials do not reside
in device configuration committed to the repository.

## Failure Boundaries

| Failure | Effect |
| --- | --- |
| CCR2004 failure | The lab loses home-network and internet connectivity. Internal lab switching and routing remain available. |
| VP6630 or VyOS failure | Routed lab segments lose their gateways, inter-segment routing, policy enforcement, and internet egress. |
| MikroTik switch failure | Devices connected through the switch lose Layer 2 connectivity. |
| Routed transit failure | Home-to-lab and lab-to-internet traffic stop. Internal lab traffic remains available within its unaffected Layer 2 and Layer 3 paths. |
| VyOS-to-MikroTik trunk failure | VLANs carried by the trunk lose their VyOS gateways. |
| Invalid configuration | Deployment verification fails and the previous configuration is restored. |

## Verification

A deployment is valid when the observed behavior matches these checks:

- Every connected interface reports the assigned link state and speed.
- Each VLAN is present only on its assigned access ports and trunks.
- A client in each routed segment reaches its VyOS gateway.
- The CCR2004 and VyOS route tables contain the required transit and lab routes.
- Home-to-lab traffic retains its home-network source address.
- Lab-to-internet traffic uses the VyOS source-NAT address.
- Each permitted firewall flow succeeds.
- Each denied firewall flow fails.
- Established reply traffic succeeds without enabling a new reverse flow.
- Management access succeeds only from approved source networks.
- A failed deployment restores the previous configuration.
