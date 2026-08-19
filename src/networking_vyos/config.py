"""Paths, connection defaults, and inventory data for gw01."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from networking_vyos.errors import ToolError

DEFAULT_HOST = "10.0.0.2"
DEFAULT_SSH_USER = "vyos"
DEFAULT_SSH_KEY = "~/.ssh/vyos-gateway"
DEFAULT_KNOWN_HOSTS = "~/.ssh/known_hosts"

TEMPLATE_SENTINELS = ("@@VYOS_PUBLIC_KEY@@",)
SENTINEL_PUBLIC_KEY = "@@VYOS_PUBLIC_KEY@@"

SSH_SOPS_RELATIVE = Path("network/vyos/ssh.sops.yaml")

TEMPLATE_RELATIVE = Path("vyos/gw01/config.boot.tmpl")
COREDNS_ASSET_RELATIVE = Path("vyos/gw01/assets/coredns/Corefile")
MIRROR_SCRIPT_ASSET_RELATIVE = Path("vyos/gw01/assets/scripts/dns-mirror-fetch-glab-lol.sh")

REMOTE_COREDNS_DIR = "/config/containers/coredns"
REMOTE_COREDNS_ZONES_DIR = "/config/containers/coredns/zones"
REMOTE_SCRIPTS_DIR = "/config/scripts"
REMOTE_COREDNS_COREFILE = "/config/containers/coredns/Corefile"
REMOTE_MIRROR_SCRIPT = "/config/scripts/dns-mirror-fetch-glab-lol.sh"
REMOTE_TAILSCALE_STATE_DIR = "/config/containers/tailscale/state"

LOCK_RELATIVE = Path(".moon/cache/gw01.lock")
HOSTNAME = "gw01"


def repo_root() -> Path:
    """Return the networking repository root that owns ``moon.yml``."""

    configured = os.environ.get("NETWORKING_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()

    here = Path(__file__).resolve()
    for candidate in (here.parent, *here.parents):
        if (candidate / "moon.yml").is_file() and (candidate / "pyproject.toml").is_file():
            return candidate
    raise ToolError("could not locate the networking repository root")


def secrets_dir() -> Path:
    """Return the explicit SOPS root from ``GLAB_SECRETS_DIR``."""

    raw = os.environ.get("GLAB_SECRETS_DIR", "").strip()
    if not raw:
        raise ToolError("GLAB_SECRETS_DIR must be set to the secrets repository root")
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise ToolError("GLAB_SECRETS_DIR is not a directory")
    return path


def expand_path(value: str) -> Path:
    return Path(value).expanduser()


@dataclass(frozen=True, slots=True)
class Connection:
    host: str
    ssh_user: str
    ssh_key: Path
    known_hosts: Path

    def pyinfra_data(self) -> dict[str, object]:
        return {
            "ssh_hostname": self.host,
            "ssh_user": self.ssh_user,
            "ssh_key": str(self.ssh_key),
            "ssh_known_hosts_file": str(self.known_hosts),
            "ssh_strict_host_key_checking": "yes",
            "ssh_look_for_keys": False,
            "networking_root": str(repo_root()),
        }


def connection_from_sources(
    *,
    host: str | None = None,
    ssh_user: str | None = None,
    ssh_key: str | None = None,
    known_hosts: str | None = None,
) -> Connection:
    """Resolve connection settings: flags, then environment, then defaults."""

    resolved_host = _first(host, os.environ.get("VYOS_HOST"), DEFAULT_HOST)
    resolved_user = _first(ssh_user, os.environ.get("VYOS_SSH_USER"), DEFAULT_SSH_USER)
    resolved_key = expand_path(_first(ssh_key, os.environ.get("VYOS_SSH_KEY"), DEFAULT_SSH_KEY))
    resolved_known_hosts = expand_path(
        _first(known_hosts, os.environ.get("VYOS_KNOWN_HOSTS"), DEFAULT_KNOWN_HOSTS)
    )
    return Connection(
        host=resolved_host,
        ssh_user=resolved_user,
        ssh_key=resolved_key,
        known_hosts=resolved_known_hosts,
    )


def apply_connection_env(connection: Connection) -> None:
    """Export resolved connection values for child pyinfra processes."""

    os.environ["VYOS_HOST"] = connection.host
    os.environ["VYOS_SSH_USER"] = connection.ssh_user
    os.environ["VYOS_SSH_KEY"] = str(connection.ssh_key)
    os.environ["VYOS_KNOWN_HOSTS"] = str(connection.known_hosts)
    os.environ["NETWORKING_ROOT"] = str(repo_root())


def _first(*values: str | None) -> str:
    for value in values:
        if value is not None and value.strip():
            return value.strip()
    raise ToolError("connection value is empty")
