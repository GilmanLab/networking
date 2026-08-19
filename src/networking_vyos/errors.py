"""Secret-safe operator errors."""

from __future__ import annotations


class ToolError(Exception):
    """User-facing failure that must never carry decrypted secret material."""
