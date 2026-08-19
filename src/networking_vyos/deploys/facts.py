"""Collect Version, redacted ConfigurationCommands, and PendingSave."""

from __future__ import annotations

import json
import os
from pathlib import Path

from pyinfra import host
from pyinfra.operations import python
from pyinfra_vyos import ConfigurationCommands, PendingSave, Version

from networking_vyos.errors import ToolError
from networking_vyos.redact import sanitize_fact_commands


def _emit_facts() -> None:
    version = host.get_fact(Version)
    if not version or not version.get("version"):
        raise ToolError("facts collection could not read Version")
    commands = host.get_fact(ConfigurationCommands, strip_private=True)
    payload = {
        "version": version,
        "commands": sanitize_fact_commands(commands),
        "pending_save": host.get_fact(PendingSave),
    }
    dest = os.environ.get("NETWORKING_FACTS_PATH", "").strip()
    if not dest:
        raise ToolError("NETWORKING_FACTS_PATH must be set for facts collection")
    Path(dest).write_text(json.dumps(payload), encoding="utf-8")


python.call(
    name="Collect redacted gw01 facts",
    function=_emit_facts,
)
