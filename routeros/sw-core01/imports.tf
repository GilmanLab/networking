# Deleted after the adoption apply. Live RouterOS item IDs (*HEX) are filled
# from the device before that apply wherever name-based addressing is not
# unique; name-based IDs follow the provider import docs.

import {
  to = routeros_interface_bridge.lab
  id = "name=bridge-lab"
}

import {
  to = routeros_interface_bridge_port.sfp_sfpplus1
  id = "interface=sfp-sfpplus1"
}

import {
  to = routeros_interface_bridge_port.sfp_sfpplus2
  id = "interface=sfp-sfpplus2"
}

import {
  to = routeros_interface_bridge_port.sfp_sfpplus3
  id = "interface=sfp-sfpplus3"
}

import {
  to = routeros_interface_bridge_port.sfp_sfpplus4
  id = "interface=sfp-sfpplus4"
}

import {
  to = routeros_interface_bridge_port.sfp_sfpplus8
  id = "interface=sfp-sfpplus8"
}

import {
  to = routeros_interface_bridge_vlan.vlan10
  # TODO(adoption): fill live ID
  # :put [/interface/bridge/vlan get [print show-ids]]
  id = "*TODO"
}

import {
  to = routeros_interface_bridge_vlan.vlan40
  # TODO(adoption): fill live ID
  # :put [/interface/bridge/vlan get [print show-ids]]
  id = "*TODO"
}

import {
  to = routeros_interface_vlan.mgmt
  id = "name=mgmt-vlan10"
}

import {
  to = routeros_ip_address.mgmt
  id = "address=10.10.10.2/24"
}

import {
  to = routeros_ip_route.default
  # TODO(adoption): fill live ID if dst_address is not unique
  # :put [/ip/route get [print show-ids]]
  id = "dst_address=0.0.0.0/0"
}

import {
  to = routeros_ip_service.www_ssl
  id = "www-ssl"
}

import {
  to = routeros_ip_service.ssh
  id = "ssh"
}

import {
  to = routeros_ip_service.winbox
  id = "winbox"
}

import {
  to = routeros_ip_service.www
  id = "www"
}

import {
  to = routeros_ip_service.ftp
  id = "ftp"
}

import {
  to = routeros_ip_service.telnet
  id = "telnet"
}

import {
  to = routeros_ip_service.api
  id = "api"
}

import {
  to = routeros_ip_service.api_ssl
  id = "api-ssl"
}

import {
  to = routeros_system_user_group.tofu_svc
  id = "name=tofu-svc"
}
