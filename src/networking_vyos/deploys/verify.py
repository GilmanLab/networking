"""Fresh-process verification of accepted gw01 state."""

from __future__ import annotations

import subprocess
import time

from pyinfra import host
from pyinfra.operations import python
from pyinfra_vyos import ConfigurationCommands, PendingSave, Version

from networking_vyos.errors import ToolError
from networking_vyos.verify import (
    require_pending_save_known,
    verify_commands,
    verify_operational_state,
)

_OP_WRAPPER = "/opt/vyatta/bin/vyatta-op-cmd-wrapper"


def _run_op(command: str) -> str:
    status, output = host.run_shell_command(command=f"{_OP_WRAPPER} {command}")
    if not status:
        raise ToolError(f"verification command failed: {command}")
    return output.stdout


def _wait_for_operational_state() -> None:
    interfaces = _run_op("show interfaces")
    routes = _run_op("show ip route")
    last_error: ToolError | None = None
    for attempt in range(12):
        try:
            verify_operational_state(
                interfaces=interfaces,
                routes=routes,
                containers=_run_op("show container"),
                stage="verification",
            )
            return
        except ToolError as error:
            last_error = error
            if attempt < 11:
                time.sleep(5)
    if last_error is not None:
        raise last_error


def _wait_for_dns(resolver: str) -> None:
    for attempt in range(12):
        try:
            completed = subprocess.run(
                [
                    "dig",
                    "+time=2",
                    "+tries=1",
                    f"@{resolver}",
                    "glab.lol",
                    "SOA",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            raise ToolError("verification requires dig on the controller") from error
        if (
            completed.returncode == 0
            and "status: NOERROR" in completed.stdout
            and "ANSWER: 1" in completed.stdout
        ):
            return
        if attempt < 11:
            time.sleep(5)
    raise ToolError(f"verification DNS probe failed through {resolver}")


def _verify_after_commit() -> None:
    version = host.get_fact(Version)
    if not version or not version.get("version"):
        raise ToolError("verification could not read Version")
    commands = host.get_fact(ConfigurationCommands, strip_private=False)
    verify_commands(commands, stage="verification")
    require_pending_save_known(
        host.get_fact(PendingSave),
        stage="verification",
    )
    _wait_for_operational_state()
    _wait_for_dns("10.10.10.54")
    _wait_for_dns("10.10.10.1")


python.call(
    name="Verify accepted gw01 configuration and runtime behavior",
    function=_verify_after_commit,
)
