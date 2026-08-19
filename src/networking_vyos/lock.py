"""Exclusive local lock for gw01 mutation."""

from __future__ import annotations

import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from networking_vyos.config import LOCK_RELATIVE, repo_root
from networking_vyos.errors import ToolError


@contextmanager
def exclusive_gw01_lock() -> Iterator[None]:
    """Hold a fail-fast exclusive lock for the local controller."""

    path = repo_root() / LOCK_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ToolError("another gw01 operation already holds the exclusive lock") from error
        yield
    finally:
        handle.close()


def lock_path() -> Path:
    return repo_root() / LOCK_RELATIVE
