terraform {
  backend "s3" {
    key          = "networking/routeros/sw-core01.tfstate"
    region       = "us-west-2"
    encrypt      = true
    use_lockfile = true
  }
}
