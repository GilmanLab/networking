resource "routeros_interface_ethernet" "ether1" {
  factory_name = "ether1"
  name         = "ether1"
  disabled     = true
  comment      = "unused"
}

resource "routeros_interface_ethernet" "sfp_sfpplus1" {
  factory_name = "sfp-sfpplus1"
  name         = "sfp-sfpplus1"
  comment      = "lab01 SFP right (PHY-012)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus2" {
  factory_name = "sfp-sfpplus2"
  name         = "sfp-sfpplus2"
  comment      = "lab01 SFP left (PHY-013)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus3" {
  factory_name = "sfp-sfpplus3"
  name         = "sfp-sfpplus3"
  comment      = "lab02 SFP right (PHY-014)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus4" {
  factory_name = "sfp-sfpplus4"
  name         = "sfp-sfpplus4"
  comment      = "lab02 SFP left (PHY-015)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus5" {
  factory_name = "sfp-sfpplus5"
  name         = "sfp-sfpplus5"
  comment      = "lab03 SFP right (PHY-016)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus6" {
  factory_name = "sfp-sfpplus6"
  name         = "sfp-sfpplus6"
  comment      = "lab03 SFP left (PHY-017)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus7" {
  factory_name = "sfp-sfpplus7"
  name         = "sfp-sfpplus7"
  comment      = "nas01 (PHY-018)"
}

resource "routeros_interface_ethernet" "sfp_sfpplus8" {
  factory_name = "sfp-sfpplus8"
  name         = "sfp-sfpplus8"
  comment      = "gw01 trunk (PHY-002)"
}
