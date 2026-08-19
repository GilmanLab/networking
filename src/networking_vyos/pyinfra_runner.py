"""Separate-process pyinfra invocations for facts and mutation stages."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

from networking_vyos.config import repo_root
from networking_vyos.errors import ToolError

DEPLOY_DIR = Path("src/networking_vyos/deploys")
INVENTORY = DEPLOY_DIR / "inventory.py"
FACTS = DEPLOY_DIR / "facts.py"
PREFLIGHT = DEPLOY_DIR / "preflight.py"
ASSETS = DEPLOY_DIR / "assets.py"
FOOTER = DEPLOY_DIR / "footer.py"
COMMIT = DEPLOY_DIR / "commit.py"
AUTH = DEPLOY_DIR / "auth.py"
VERIFY = DEPLOY_DIR / "verify.py"
SAVE = DEPLOY_DIR / "save.py"
FINAL = DEPLOY_DIR / "final.py"

SYNC_STAGES: tuple[tuple[str, Path], ...] = (
    ("preflight", PREFLIGHT),
    ("assets", ASSETS),
    ("footer", FOOTER),
    ("commit", COMMIT),
    ("auth", AUTH),
    ("verify", VERIFY),
    ("save", SAVE),
    ("final", FINAL),
)


def run_pyinfra(deploy: Path, *, extra_env: dict[str, str] | None = None) -> None:
    """Run one deploy file in a fresh pyinfra process."""

    command = [
        sys.executable,
        "-m",
        "pyinfra",
        str(INVENTORY),
        str(deploy),
        "--yes",
        "--chdir",
        str(repo_root()),
    ]
    env = os.environ.copy()
    env["PYINFRA_PROGRESS"] = "off"
    if extra_env:
        env.update(extra_env)
    completed = subprocess.run(
        command,
        check=False,
        cwd=repo_root(),
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    if completed.returncode != 0:
        raise ToolError(f"pyinfra {deploy.name} failed")


def collect_facts() -> dict[str, object]:
    """Collect Version, redacted ConfigurationCommands, and PendingSave."""

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as handle:
        path = Path(handle.name)
    try:
        run_pyinfra(FACTS, extra_env={"NETWORKING_FACTS_PATH": str(path)})
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ToolError("facts collection did not emit JSON") from error
        if not isinstance(payload, dict):
            raise ToolError("facts JSON was not an object")
        return payload
    finally:
        path.unlink(missing_ok=True)


def run_sync_stages(
    runner: Callable[[Path], None] | None = None,
) -> list[str]:
    """Run each sync stage in its own process and return the completed names."""

    execute = runner or run_pyinfra
    completed: list[str] = []
    for name, deploy in SYNC_STAGES:
        execute(deploy)
        completed.append(name)
    return completed


def stage_names() -> Sequence[str]:
    return tuple(name for name, _ in SYNC_STAGES)
