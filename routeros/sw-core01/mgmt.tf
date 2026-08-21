resource "routeros_interface_vlan" "mgmt" {
  interface = routeros_interface_bridge.lab.name
  name      = "mgmt-vlan10"
  vlan_id   = 10
}

resource "routeros_ip_address" "mgmt" {
  address   = "10.10.10.2/24"
  interface = routeros_interface_vlan.mgmt.name
}

resource "routeros_ip_dns" "mgmt" {
  servers = ["10.10.10.1"]
}

resource "routeros_ip_route" "default" {
  dst_address = "0.0.0.0/0"
  gateway     = "10.10.10.1"
}

resource "routeros_system_ntp_client" "mgmt" {
  enabled = true
  servers = ["10.10.10.1"]
}
