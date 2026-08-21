resource "routeros_system_identity" "this" {
  name = "sw-core01"
}

# Changing this group's policy can cut tofu's own REST session.
# RouterOS REST authenticates via the binary api, so `api` is required
# alongside `rest-api`.
resource "routeros_system_user_group" "tofu_svc" {
  name    = "tofu-svc"
  comment = "Changing this group can cut tofu's own session."
  policy  = ["read", "write", "api", "rest-api"]
}
