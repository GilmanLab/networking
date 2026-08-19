"""Capture the live restore footer from gw01 /config/config.boot."""

from __future__ import annotations

from pyinfra import host
from pyinfra.operations import python

from networking_vyos.errors import ToolError
from networking_vyos.footer import footer_env_path, write_captured_footer

_FOOTER_COMMAND = r"sudo sed -n '/^\/\/ Warning:/,$p' /config/config.boot"


def _capture_footer() -> None:
    status, output = host.run_shell_command(command=_FOOTER_COMMAND)
    if not status:
        raise ToolError("failed to capture the live gw01 footer")
    write_captured_footer(output.stdout, footer_env_path())


python.call(
    name="Capture live restore footer from /config/config.boot",
    function=_capture_footer,
)
