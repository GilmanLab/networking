"""Fresh final check requiring PendingSave is False after save."""

from __future__ import annotations

from pyinfra import host
from pyinfra.operations import python
from pyinfra_vyos import ConfigurationCommands, PendingSave, Version

from networking_vyos.errors import ToolError
from networking_vyos.verify import require_pending_save, verify_commands


def _final_check() -> None:
    version = host.get_fact(Version)
    if not version or not version.get("version"):
        raise ToolError("final check could not read Version")
    commands = host.get_fact(ConfigurationCommands, strip_private=False)
    verify_commands(commands, stage="final check")
    require_pending_save(host.get_fact(PendingSave), expected=False, stage="final check")


python.call(
    name="Require saved accepted state after persist",
    function=_final_check,
)
