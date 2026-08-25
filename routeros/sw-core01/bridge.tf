resource "routeros_interface_bridge" "lab" {
  name           = "bridge-lab"
  vlan_filtering = true
}

resource "routeros_interface_bridge_port" "bond_lab01" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_bonding.bond_lab01.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "bond_lab02" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_bonding.bond_lab02.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "bond_lab03" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_bonding.bond_lab03.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus7" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus7.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus8" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus8.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_vlan" "vlan10" {
  bridge   = routeros_interface_bridge.lab.name
  vlan_ids = ["10"]
  tagged = [
    routeros_interface_bridge.lab.name,
    routeros_interface_ethernet.sfp_sfpplus8.name,
  ]
}

resource "routeros_interface_bridge_vlan" "vlan30" {
  bridge   = routeros_interface_bridge.lab.name
  vlan_ids = ["30"]
  tagged = [
    routeros_interface_bonding.bond_lab01.name,
    routeros_interface_bonding.bond_lab02.name,
    routeros_interface_bonding.bond_lab03.name,
    routeros_interface_ethernet.sfp_sfpplus7.name,
  ]
}

resource "routeros_interface_bridge_vlan" "vlan40" {
  bridge   = routeros_interface_bridge.lab.name
  vlan_ids = ["40"]
  tagged = [
    routeros_interface_ethernet.sfp_sfpplus8.name,
  ]
}
