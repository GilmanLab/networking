---
title: Hardware
description: Known core-network equipment and the evidence that supports each fact.
---

# Hardware

This reference separates repository evidence from facts verified on the physical
devices. Lab v1 files identify the intended equipment and interface mapping.
Lab v2 has not yet confirmed that mapping on the devices.

## Known equipment

| Component | Known fact | Evidence status |
| --- | --- | --- |
| VyOS gateway | The Lab v1 gateway configuration targets a Minisforum VP6630. Lab v2 assigns Layer 3 routing and policy to VyOS. | Repository evidence; physical model and interfaces require verification. |
| MikroTik switch | Lab v1 used a MikroTik switch. Lab v2 assigns Layer 2 switching and VLAN transport to MikroTik. | Role established; exact model and port layout require verification. |
| Home router | Lab v1 identifies a MikroTik CCR2004 on the home side of the lab transit. | Legacy evidence; Lab v2 device and interface require verification. |

The sources are the Lab v1
[gateway configuration](https://github.com/GilmanLab/lab/blob/master/infrastructure/network/vyos/configs/gateway.conf)
and
[network description](https://github.com/GilmanLab/lab/blob/master/docs/architecture/08_concepts/networking.md).

## Legacy VP6630 interface mapping

The Lab v1 gateway configuration records this mapping:

| VyOS interface | Legacy physical description | Legacy role |
| --- | --- | --- |
| `eth0` | Top SFP+ port | Transit to the home router |
| `eth1` | Bottom SFP+ port | Trunk to the MikroTik switch |
| `eth2` through `eth5` | 2.5 GbE ports | Direct lab connections |

Do not use this mapping for Lab v2 deployment until an on-device inventory
confirms the interface names, MAC addresses, media, and cable endpoints.

## Facts required before design acceptance

Verify and record:

- Manufacturer and exact model for each managed device
- Installed operating-system or firmware version
- Interface names and MAC addresses
- Media type and supported speed for each physical port
- Current cable endpoint and negotiated speed for each connected port
- Available console or out-of-band recovery path
- Power and restart behavior

After verification, replace the evidence-status statements with observed values
and record the observation date.
