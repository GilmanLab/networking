# sw-core01

OpenTofu root for the lab core switch (`sw-core01`, MikroTik CRS309-1G-8S+).
State lives at `s3://$GLAB_AWS_STATE_BUCKET/networking/routeros/sw-core01.tfstate`.

The bootstrap runbook that produces the TLS pin, service account, and first
adoption is `docs/docs/runbooks/sw-core01-configuration.md` in the meta
repository.

## Prerequisites

- `tofu` >= 1.10
- `just`
- `sops`
- SSH access as `admin@10.10.10.2` for snapshots
- Network reach to `10.10.10.2`

Export these from the workspace `.envrc` before `init`/`plan`/`apply`:

```sh
export AWS_PROFILE=lab-admin
export GLAB_AWS_STATE_BUCKET=glab-lab-tfstate-186067932323
export GLAB_SECRETS_DIR=/path/to/GilmanLab/secrets
```

`just plan` and `just apply` decrypt `username`/`password` from
`$GLAB_SECRETS_DIR/network/sw-core01/terraform.sops.yaml` into
`ROS_USERNAME`/`ROS_PASSWORD`. Those values are never Terraform variables.

## Certificate pin

`certs/sw-core01-ca.crt` is the on-device local CA (`CN=sw-core01-ca`) that
signs the `sw-core01-tls` leaf. The provider `ca_certificate` points at this
file. RouterOS 7.16 cannot self-sign a leaf, so the pin is the CA, not the
leaf. Certificate lifecycle remains runbook-owned.

## Plan and apply

```sh
just check
just init
just snapshot
just plan
just apply
```

Run `just snapshot` before every apply. RouterOS has no commit-confirmed, and
Safe Mode does not cover REST.

`just check` is offline (`fmt -check`, `init -backend=false`, `validate`).
CI never decrypts secrets and never contacts the device.

## Drift

Run `just plan` before every change, after any RouterOS upgrade, and ad hoc.
There is no CI drift job.

## First apply of lab LACP + VLAN 30

RouterOS rejects enslaving an interface that is still a bridge port.
terraform-routeros v1.99.1 bonding Create is a plain REST POST; it does
not unslave first. `depends_on` cannot name the six `sfp-sfpplus1`–`6`
bridge-port resources this change deletes, so OpenTofu will not destroy
those orphans before creating the bonds.

An untargeted plan of this change is **7 to add, 6 to destroy**. Do not
apply that mixed plan: RouterOS will reject the bond creates while the
old port rows still exist.

1. Snapshot, then destroy only the six per-port rows (they are already
   absent from this configuration and remain only in state):

   ```sh
   just snapshot
   tofu apply \
     -target=routeros_interface_bridge_port.sfp_sfpplus1 \
     -target=routeros_interface_bridge_port.sfp_sfpplus2 \
     -target=routeros_interface_bridge_port.sfp_sfpplus3 \
     -target=routeros_interface_bridge_port.sfp_sfpplus4 \
     -target=routeros_interface_bridge_port.sfp_sfpplus5 \
     -target=routeros_interface_bridge_port.sfp_sfpplus6
   ```

   Expected plan: **6 to destroy**.

2. Create the bonds, their bridge ports, and VLAN 30:

   ```sh
   just snapshot
   just plan
   just apply
   ```

   Expected plan: **7 to add** (3 bonds, 3 bond bridge ports, 1 VLAN 30
   row). No changes to `bridge-lab`, port 8, VLAN 10, VLAN 40, or the
   mgmt address/route.

VLAN 30 is L2-only. It is tagged on `bond-lab01`–`03` and `sfp-sfpplus7`
(nas01). It is not tagged on `bridge-lab` or the gw01 trunk
(`sfp-sfpplus8`).

## Notes

- Ethernet names stay at factory (`ether1`, `sfp-sfpplus1`–`8`). Roles and
  PHY IDs live in comments.
- `ether1` is disabled (`comment = "unused"`).
- Users, passwords, and the `sw-core01-tls` leaf certificate are
  runbook-owned. The `svc-tofu` user is restricted to
  `10.10.10.0/24,192.168.1.0/24,100.64.0.0/10`.
- Delete `imports.tf` after the adoption apply.
