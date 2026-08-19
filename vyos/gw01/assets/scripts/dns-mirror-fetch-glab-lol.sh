#!/bin/sh
set -eu

podman run --rm \
  --network host \
  --volume /config/containers/coredns/zones:/zones \
  ghcr.io/gilmanlab/platform/services/dns-mirror:0.3.1 \
  fetch \
  --source-url http://100.80.89.100:8080/zonefile \
  --output-path /zones/glab.lol.zone \
  --timeout 15s

chmod 0644 /config/containers/coredns/zones/glab.lol.zone
