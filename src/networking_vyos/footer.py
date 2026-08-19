"""Live VyOS restore footer captured from gw01, never invented."""

from __future__ import annotations

import os
from pathlib import Path

from networking_vyos.errors import ToolError

WARNING_LINE = "// Warning: Do not remove the following line."
VERSION_PREFIX = "// vyos-config-version:"
RELEASE_PREFIX = "// Release version:"


def footer_env_path() -> Path:
    raw = os.environ.get("NETWORKING_FOOTER_PATH", "").strip()
    if not raw:
        raise ToolError("NETWORKING_FOOTER_PATH must be set to a captured footer file")
    return Path(raw)


def validate_footer(footer: str) -> None:
    """Refuse an empty, partial, or invented-looking footer."""

    if not footer.strip():
        raise ToolError("captured gw01 footer is empty")
    if WARNING_LINE not in footer:
        raise ToolError("captured gw01 footer is missing the Warning line")
    if VERSION_PREFIX not in footer:
        raise ToolError("captured gw01 footer is missing // vyos-config-version")
    if RELEASE_PREFIX not in footer:
        raise ToolError("captured gw01 footer is missing // Release version")
    if "@@" in footer:
        raise ToolError("captured gw01 footer contains unresolved sentinels")


def load_captured_footer() -> str:
    path = footer_env_path()
    try:
        footer = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ToolError("cannot read captured gw01 footer") from error
    validate_footer(footer)
    return footer


def write_captured_footer(footer: str, path: Path) -> None:
    validate_footer(footer)
    path.write_text(footer if footer.endswith("\n") else f"{footer}\n", encoding="utf-8")
