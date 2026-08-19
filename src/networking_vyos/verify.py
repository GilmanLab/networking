"""Assertions over unredacted configuration commands and pending-save state."""

from __future__ import annotations

from collections.abc import Iterable

from networking_vyos.errors import ToolError

REQUIRED_LINE_FRAGMENTS: tuple[tuple[str, ...], ...] = (
    ("set system host-name", "gw01"),
    ("set interfaces ethernet eth0 address", "10.0.0.2/30"),
    ("set interfaces bridge br10 address", "10.10.10.1/24"),
    ("set interfaces bridge br40 address", "10.10.40.1/24"),
    ("set interfaces bridge br70 address", "10.10.70.1/24"),
    ("set interfaces ethernet eth1 vif 10",),
    ("set interfaces ethernet eth1 vif 40",),
    ("set interfaces ethernet eth3 vif 10",),
    ("set interfaces ethernet eth3 vif 70",),
    ("set interfaces bridge br10 member interface eth3.10",),
    ("set interfaces bridge br40 member interface eth2",),
    ("set interfaces bridge br70 member interface eth3.70",),
    ("set protocols static route", "0.0.0.0/0", "10.0.0.1"),
    ("set service dhcp-server",),
    ("set service dhcp-server listen-interface", "br10"),
    ("set service dhcp-server listen-interface", "br40"),
    ("set service dhcp-server listen-interface", "br70"),
    ("set container name tailscale environment TS_ROUTES value", "10.10.0.0/16"),
    ("set container name tailscale",),
    ("set container name coredns-glab-lol",),
    ("set firewall ipv4 forward filter default-action", "drop"),
    ("set firewall ipv4 input filter default-action", "drop"),
    ("set firewall ipv4 forward filter rule 100 inbound-interface name", "eth0"),
    ("set firewall ipv4 forward filter rule 100 jump-target", "WAN_FORWARD"),
    ("set firewall ipv4 forward filter rule 110 inbound-interface name", "br10"),
    ("set firewall ipv4 forward filter rule 110 jump-target", "MGMT_FORWARD"),
    ("set firewall ipv4 forward filter rule 120 inbound-interface name", "br40"),
    ("set firewall ipv4 forward filter rule 120 jump-target", "SANDBOX_FORWARD"),
    ("set firewall ipv4 forward filter rule 130 inbound-interface name", "br70"),
    ("set firewall ipv4 forward filter rule 130 jump-target", "OOB_FORWARD"),
    ("set firewall ipv4 input filter rule 100 inbound-interface name", "eth0"),
    ("set firewall ipv4 input filter rule 100 jump-target", "WAN_LOCAL"),
    ("set firewall ipv4 input filter rule 110 inbound-interface name", "br10"),
    ("set firewall ipv4 input filter rule 110 jump-target", "MGMT_LOCAL"),
    ("set firewall ipv4 input filter rule 120 inbound-interface name", "br40"),
    ("set firewall ipv4 input filter rule 120 jump-target", "SANDBOX_LOCAL"),
    ("set firewall ipv4 input filter rule 130 inbound-interface name", "br70"),
    ("set firewall ipv4 input filter rule 130 jump-target", "OOB_LOCAL"),
)

RETIRED_FRAGMENTS = (
    "vif 20",
    "10.10.20.",
    "tinkerbell",
    "pdns-auth",
    "powerdns",
    "lab.gilman.io",
    "incusos-artifacts",
    "bootstrap-k0s",
    "service dns forwarding",
    "protocols bgp",
    "bridge br20",
    "host-name 'gateway'",
    "host-name gateway",
)


def normalize_commands(commands: Iterable[object]) -> list[str]:
    return [str(line) for line in commands]


def require_pending_save(value: object, *, expected: bool, stage: str) -> None:
    if value is not expected:
        raise ToolError(f"{stage} requires PendingSave is {expected}")


def require_pending_save_known(value: object, *, stage: str) -> None:
    if value is None:
        raise ToolError(f"{stage} could not determine PendingSave")


def _line_matches(line: str, fragments: tuple[str, ...]) -> bool:
    return all(fragment in line for fragment in fragments)


def verify_commands(commands: Iterable[object], *, stage: str) -> None:
    lines = normalize_commands(commands)
    blob = "\n".join(lines).lower()
    for fragments in REQUIRED_LINE_FRAGMENTS:
        if not any(_line_matches(line, fragments) for line in lines):
            raise ToolError(f"{stage} is missing required configuration: {' '.join(fragments)}")
    for fragment in RETIRED_FRAGMENTS:
        if fragment.lower() in blob:
            raise ToolError(f"{stage} still contains retired state: {fragment}")


def verify_operational_state(
    *,
    interfaces: str,
    routes: str,
    containers: str,
    stage: str,
) -> None:
    required_interfaces = (
        ("eth0", "10.0.0.2/30"),
        ("br10", "10.10.10.1/24"),
        ("br40", "10.10.40.1/24"),
        ("br70", "10.10.70.1/24"),
    )
    for fragments in required_interfaces:
        if not any(
            all(fragment in line for fragment in fragments) for line in interfaces.splitlines()
        ):
            raise ToolError(f"{stage} is missing an active interface: {' '.join(fragments)}")

    if not any("0.0.0.0/0" in line and "10.0.0.1" in line for line in routes.splitlines()):
        raise ToolError(f"{stage} is missing the active default route")

    for name in ("coredns-glab-lol", "tailscale"):
        matching = [line for line in containers.splitlines() if name in line]
        if not matching or not any("up" in line.casefold() for line in matching):
            raise ToolError(f"{stage} container is not running: {name}")
