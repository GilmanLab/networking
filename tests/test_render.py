from __future__ import annotations

from io import StringIO

import pytest
from conftest import LIVE_FOOTER, VALID_TEMPLATE

from networking_vyos.errors import ToolError
from networking_vyos.render import render_config
from networking_vyos.secrets import RenderSecrets

SECRETS = RenderSecrets(public_key="AAAAPUBLIC")


def test_render_replaces_each_sentinel_once_and_appends_footer() -> None:
    rendered = render_config(VALID_TEMPLATE, SECRETS, LIVE_FOOTER)
    assert "@@VYOS_PUBLIC_KEY@@" not in rendered
    assert "AAAAPUBLIC" in rendered
    assert rendered.endswith(
        "// Warning: Do not remove the following line.\n"
        '// vyos-config-version: "broadcast-relay@1:cluster@2"\n'
        "// Release version: 1.5.0\n"
    )


def test_render_rejects_missing_sentinel() -> None:
    with pytest.raises(ToolError, match="exactly one @@VYOS_PUBLIC_KEY@@"):
        render_config(
            VALID_TEMPLATE.replace("@@VYOS_PUBLIC_KEY@@", "missing"), SECRETS, LIVE_FOOTER
        )


def test_render_rejects_duplicate_sentinel() -> None:
    with pytest.raises(ToolError, match="exactly one @@VYOS_PUBLIC_KEY@@"):
        render_config(VALID_TEMPLATE + "\n@@VYOS_PUBLIC_KEY@@\n", SECRETS, LIVE_FOOTER)


def test_render_rejects_unknown_sentinel() -> None:
    with pytest.raises(ToolError, match="unresolved sentinels"):
        render_config(VALID_TEMPLATE.replace("gw01", "@@UNKNOWN@@"), SECRETS, LIVE_FOOTER)


def test_render_rejects_missing_live_footer() -> None:
    with pytest.raises(ToolError, match="Warning line"):
        render_config(VALID_TEMPLATE, SECRETS, "// incomplete\n")


def test_rendered_config_stays_in_memory() -> None:
    from networking_vyos import render as render_mod

    original = render_mod.load_template
    render_mod.load_template = lambda: VALID_TEMPLATE
    try:
        handle = render_mod.rendered_config_file(SECRETS, LIVE_FOOTER)
    finally:
        render_mod.load_template = original
    assert isinstance(handle, StringIO)
    assert handle.tell() == 0
    assert "AAAAPUBLIC" in handle.read()
