provider "routeros" {
  hosturl        = "https://10.10.10.2"
  ca_certificate = "${path.module}/certs/sw-core01-ca.crt"
  # username/password from ROS_USERNAME / ROS_PASSWORD env — never variables
}
