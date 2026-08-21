resource "routeros_ip_service" "www_ssl" {
  numbers     = "www-ssl"
  port        = 443
  certificate = "sw-core01-tls"
  address     = "10.10.10.0/24,192.168.1.0/24,100.64.0.0/10"
  disabled    = false
}

resource "routeros_ip_service" "ssh" {
  numbers  = "ssh"
  port     = 22
  address  = "10.10.10.0/24,192.168.1.0/24,100.64.0.0/10"
  disabled = false
}

resource "routeros_ip_service" "winbox" {
  numbers  = "winbox"
  port     = 8291
  address  = "10.10.10.0/24,192.168.1.0/24,100.64.0.0/10"
  disabled = false
}

resource "routeros_ip_service" "www" {
  numbers  = "www"
  port     = 80
  disabled = true
}

resource "routeros_ip_service" "ftp" {
  numbers  = "ftp"
  port     = 21
  disabled = true
}

resource "routeros_ip_service" "telnet" {
  numbers  = "telnet"
  port     = 23
  disabled = true
}

resource "routeros_ip_service" "api" {
  numbers  = "api"
  port     = 8728
  disabled = true
}

resource "routeros_ip_service" "api_ssl" {
  numbers  = "api-ssl"
  port     = 8729
  disabled = true
}
