"""Source-policy validation for the gw01 template."""

from __future__ import annotations

import re

from networking_vyos.config import TEMPLATE_SENTINELS
from networking_vyos.errors import ToolError

_FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bvlan\s+20\b", "VLAN20"),
    (r"\bvif\s+20\b", "VLAN20"),
    (r"\b10\.10\.20\.", "VLAN20 prefix"),
    (r"\btinkerbell\b", "Tinkerbell"),
    (r"\bpowerdns\b", "PowerDNS"),
    (r"\bpdns-auth\b", "PowerDNS"),
    (r"\blab\.gilman\.io\b", "legacy lab.gilman.io zone"),
    (r"\bincusos-artifacts\b", "artifact serving"),
    (r"\bbootstrap-k0s\b", "bootstrap-k0s"),
    (r"\bbgp\b", "BGP"),
    (r"\bbridge\s+br20\b", "UM760 bridge behavior"),
    (r"\bhost-name\s+gateway\b", "hostname gateway"),
)

_REQUIRED_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bhost-name\s+gw01\b", "hostname gw01"),
    (r"\b10\.0\.0\.2/30\b", "transit address"),
    (r"\b10\.10\.10\.1/24\b", "management gateway"),
    (r"\b10\.10\.40\.1/24\b", "sandbox gateway"),
    (r"\b10\.10\.70\.1/24\b", "OOB gateway"),
    (r"\bnext-hop\s+10\.0\.0\.1\b", "default route"),
    (r"\btailscale\b", "Tailscale"),
    (r"\bcoredns\b", "CoreDNS"),
    (r"\bdhcp-server\b", "DHCP"),
    (r"/config/config\.boot", "live footer source policy"),
)


def validate_template(template: str) -> None:
    """Refuse a template that invents a footer or retains retired state."""

    if re.search(r"(?m)^// vyos-config-version:", template):
        raise ToolError("template must not invent a // vyos-config-version footer")
    if re.search(r"(?m)^// Release version:", template):
        raise ToolError("template must not invent a // Release version footer")

    for sentinel in TEMPLATE_SENTINELS:
        if template.count(sentinel) != 1:
            raise ToolError(f"template must contain exactly one {sentinel}")

    lowered = template.lower()
    for pattern, label in _FORBIDDEN_PATTERNS:
        if re.search(pattern, lowered):
            raise ToolError(f"template still contains retired {label}")

    for pattern, label in _REQUIRED_PATTERNS:
        if not re.search(pattern, lowered):
            raise ToolError(f"template is missing required {label}")


def validate_assets_present() -> None:
    from networking_vyos.config import (
        COREDNS_ASSET_RELATIVE,
        MIRROR_SCRIPT_ASSET_RELATIVE,
        repo_root,
    )

    root = repo_root()
    for relative in (COREDNS_ASSET_RELATIVE, MIRROR_SCRIPT_ASSET_RELATIVE):
        if not (root / relative).is_file():
            raise ToolError(f"missing nonsecret asset {relative}")
