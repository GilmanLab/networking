resource "routeros_interface_bridge" "lab" {
  name           = "bridge-lab"
  vlan_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus1" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus1.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus2" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus2.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus3" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus3.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus4" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus4.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus5" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus5.name
  frame_types       = "admit-only-vlan-tagged"
  ingress_filtering = true
}

resource "routeros_interface_bridge_port" "sfp_sfpplus6" {
  bridge            = routeros_interface_bridge.lab.name
  interface         = routeros_interface_ethernet.sfp_sfpplus6.name
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

resource "routeros_interface_bridge_vlan" "vlan40" {
  bridge   = routeros_interface_bridge.lab.name
  vlan_ids = ["40"]
  tagged = [
    routeros_interface_ethernet.sfp_sfpplus8.name,
  ]
}
