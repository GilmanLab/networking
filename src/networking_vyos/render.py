"""In-memory sentinel rendering for the gw01 boot template."""

from __future__ import annotations

from io import StringIO

from networking_vyos.config import (
    SENTINEL_PUBLIC_KEY,
    TEMPLATE_RELATIVE,
    TEMPLATE_SENTINELS,
    repo_root,
)
from networking_vyos.errors import ToolError
from networking_vyos.footer import validate_footer
from networking_vyos.secrets import RenderSecrets


def load_template() -> str:
    path = repo_root() / TEMPLATE_RELATIVE
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ToolError(f"cannot read {TEMPLATE_RELATIVE}") from error


def render_config(template: str, secrets: RenderSecrets, footer: str) -> str:
    """Replace every tracked sentinel exactly once and append the live footer."""

    replacements = {SENTINEL_PUBLIC_KEY: secrets.public_key}
    rendered = template
    for sentinel, value in replacements.items():
        if rendered.count(sentinel) != 1:
            raise ToolError(f"template must contain exactly one {sentinel}")
        rendered = rendered.replace(sentinel, value, 1)

    leftover = [sentinel for sentinel in TEMPLATE_SENTINELS if sentinel in rendered]
    if leftover:
        raise ToolError("rendered configuration still contains template sentinels")
    if "@@" in rendered:
        raise ToolError("rendered configuration still contains unresolved sentinels")

    validate_footer(footer)
    if not rendered.endswith("\n"):
        rendered += "\n"
    return f"{rendered}{footer.rstrip()}\n"


def rendered_config_file(secrets: RenderSecrets, footer: str) -> StringIO:
    """Return a seekable in-memory config for ``config_load``."""

    stream = StringIO(render_config(load_template(), secrets, footer))
    stream.seek(0)
    return stream
