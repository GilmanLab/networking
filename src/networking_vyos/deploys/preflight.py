"""Read-only preflight: require PendingSave is False before mutation."""

from __future__ import annotations

from pyinfra import host
from pyinfra.operations import python
from pyinfra_vyos import PendingSave, Version

from networking_vyos.errors import ToolError
from networking_vyos.verify import require_pending_save


def _check_preflight() -> None:
    version = host.get_fact(Version)
    if not version or not version.get("version"):
        raise ToolError("preflight could not read Version")
    require_pending_save(host.get_fact(PendingSave), expected=False, stage="preflight")


python.call(
    name="Refuse unsaved device state before mutation",
    function=_check_preflight,
)
