resource "routeros_system_identity" "this" {
  name = "sw-core01"
}

# The tofu-svc group and svc-tofu user are runbook-owned: svc-tofu deliberately
# lacks the `policy` permission, so it cannot manage user groups (self-escalation
# guard), and user passwords must never enter state.
