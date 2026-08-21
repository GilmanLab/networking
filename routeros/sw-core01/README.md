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

## Notes

- Ethernet names stay at factory (`ether1`, `sfp-sfpplus1`–`8`). Roles and
  PHY IDs live in comments.
- `ether1` is disabled (`comment = "unused"`).
- Users, passwords, and the `sw-core01-tls` leaf certificate are
  runbook-owned. The `svc-tofu` user is restricted to
  `10.10.10.0/24,192.168.1.0/24,100.64.0.0/10`.
- Delete `imports.tf` after the adoption apply.
