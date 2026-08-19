"""Load the rendered boot config without saving it."""

from __future__ import annotations

from pyinfra.operations import server
from pyinfra_vyos import config_load

from networking_vyos.footer import load_captured_footer
from networking_vyos.render import rendered_config_file
from networking_vyos.secrets import load_render_secrets

server.shell(
    name="Ensure VyOS interface commit compatibility chains exist",
    commands=[
        "sudo nft list table ip raw >/dev/null 2>&1 || sudo nft add table ip raw",
        "sudo nft list chain ip raw VYOS_TCP_MSS >/dev/null 2>&1 || "
        "sudo nft add chain ip raw VYOS_TCP_MSS",
        "sudo nft list chain ip raw vyos_rpfilter >/dev/null 2>&1 || "
        "sudo nft add chain ip raw vyos_rpfilter",
        "sudo nft list table ip6 raw >/dev/null 2>&1 || sudo nft add table ip6 raw",
        "sudo nft list chain ip6 raw VYOS_TCP_MSS >/dev/null 2>&1 || "
        "sudo nft add chain ip6 raw VYOS_TCP_MSS",
        "sudo nft list chain ip6 raw vyos_rpfilter >/dev/null 2>&1 || "
        "sudo nft add chain ip6 raw vyos_rpfilter",
    ],
)

config_load(
    name="Load the rendered gw01 config without saving",
    src=rendered_config_file(load_render_secrets(), load_captured_footer()),
    save=False,
)
