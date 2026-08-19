"""Stage remaining nonsecret CoreDNS assets on gw01."""

from __future__ import annotations

from pyinfra.operations import files, server

from networking_vyos.config import (
    COREDNS_ASSET_RELATIVE,
    MIRROR_SCRIPT_ASSET_RELATIVE,
    REMOTE_COREDNS_COREFILE,
    REMOTE_COREDNS_DIR,
    REMOTE_COREDNS_ZONES_DIR,
    REMOTE_MIRROR_SCRIPT,
    REMOTE_SCRIPTS_DIR,
    REMOTE_TAILSCALE_STATE_DIR,
    repo_root,
)

_root = repo_root()

server.shell(
    name="Prepare persistent runtime directories",
    commands=[
        f"sudo install -d -m 0750 {REMOTE_COREDNS_DIR} {REMOTE_SCRIPTS_DIR}",
        f"sudo install -d -m 0755 {REMOTE_COREDNS_ZONES_DIR}",
        f"sudo install -d -m 0700 {REMOTE_TAILSCALE_STATE_DIR}",
    ],
)

server.shell(
    name="Pre-pull gateway service images",
    commands=[
        "sudo podman pull docker.io/coredns/coredns:1.13.1",
        "sudo podman pull docker.io/tailscale/tailscale:v1.96.5",
        "sudo podman pull ghcr.io/gilmanlab/platform/services/dns-mirror:0.3.1",
    ],
)

files.put(
    name="Stage CoreDNS Corefile",
    src=str(_root / COREDNS_ASSET_RELATIVE),
    dest="/tmp/gw01-Corefile",
    mode="0644",
)

files.put(
    name="Stage dns-mirror fetch script",
    src=str(_root / MIRROR_SCRIPT_ASSET_RELATIVE),
    dest="/tmp/gw01-dns-mirror-fetch-glab-lol.sh",
    mode="0755",
)

server.shell(
    name="Install staged CoreDNS assets",
    commands=[
        f"sudo install -m 0644 /tmp/gw01-Corefile {REMOTE_COREDNS_COREFILE}",
        f"sudo install -m 0755 /tmp/gw01-dns-mirror-fetch-glab-lol.sh {REMOTE_MIRROR_SCRIPT}",
        "rm -f /tmp/gw01-Corefile /tmp/gw01-dns-mirror-fetch-glab-lol.sh",
    ],
)

server.shell(
    name="Fetch the initial glab.lol mirror",
    commands=[f"sudo {REMOTE_MIRROR_SCRIPT}"],
)
