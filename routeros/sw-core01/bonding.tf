# RouterOS rejects enslaving an interface that is still a bridge port
# ("already added as bridge port"). terraform-routeros v1.99.1 bonding
# Create is a plain REST POST (DefaultCreate); it does not remove the
# slaves from /interface/bridge/port first. depends_on cannot name the
# six sfp-sfpplus1..6 bridge-port resources this change deletes, and
# OpenTofu will not order those orphan destroys before these creates.
# Apply in two steps as described in README.md.

resource "routeros_interface_bonding" "bond_lab01" {
  name                 = "bond-lab01"
  slaves               = [routeros_interface_ethernet.sfp_sfpplus1.name, routeros_interface_ethernet.sfp_sfpplus2.name]
  mode                 = "802.3ad"
  transmit_hash_policy = "layer-3-and-4"
  lacp_rate            = "30secs"
  comment              = "lab01 SFP pair (PHY-012 + PHY-013)"
}

resource "routeros_interface_bonding" "bond_lab02" {
  name                 = "bond-lab02"
  slaves               = [routeros_interface_ethernet.sfp_sfpplus3.name, routeros_interface_ethernet.sfp_sfpplus4.name]
  mode                 = "802.3ad"
  transmit_hash_policy = "layer-3-and-4"
  lacp_rate            = "30secs"
  comment              = "lab02 SFP pair (PHY-014 + PHY-015)"
}

resource "routeros_interface_bonding" "bond_lab03" {
  name                 = "bond-lab03"
  slaves               = [routeros_interface_ethernet.sfp_sfpplus5.name, routeros_interface_ethernet.sfp_sfpplus6.name]
  mode                 = "802.3ad"
  transmit_hash_policy = "layer-3-and-4"
  lacp_rate            = "30secs"
  comment              = "lab03 SFP pair (PHY-016 + PHY-017)"
}
