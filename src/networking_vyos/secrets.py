"""Strict SOPS JSON decryption for gw01 sentinels."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from networking_vyos.config import SSH_SOPS_RELATIVE, secrets_dir
from networking_vyos.errors import ToolError

_PUBLIC_KEY_KEYS = ("public_key",)
_PASSWORD_HASH_KEYS = ("password_hash",)


@dataclass(frozen=True, slots=True)
class RenderSecrets:
    public_key: str


def load_render_secrets() -> RenderSecrets:
    """Return the non-secret public-key material used by the full config load."""

    ssh = _decrypt_object(secrets_dir() / SSH_SOPS_RELATIVE, _PUBLIC_KEY_KEYS)
    return RenderSecrets(public_key=_public_key_material(ssh["public_key"]))


def load_password_hash() -> str:
    """Return the validated hash applied after the full config load."""

    ssh = _decrypt_object(secrets_dir() / SSH_SOPS_RELATIVE, _PASSWORD_HASH_KEYS)
    password_hash = _inline_value("password_hash", ssh["password_hash"])
    if not password_hash.startswith("$6$"):
        raise ToolError("password_hash must use SHA-512 crypt")
    return password_hash


def _public_key_material(public_key: str) -> str:
    parts = public_key.split()
    if len(parts) < 2 or parts[0] != "ssh-ed25519":
        raise ToolError("public_key must be an ssh-ed25519 public key")
    material = parts[1]
    if not re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", material):
        raise ToolError("public_key contains invalid key material")
    return material


def _inline_value(label: str, value: str) -> str:
    if any(character in value for character in ('"', "\\", "\r", "\n")):
        raise ToolError(f"{label} cannot be represented in a VyOS configuration command")
    return value


def _decrypt_object(path: Path, required: tuple[str, ...]) -> dict[str, str]:
    if not path.is_file():
        raise ToolError(f"missing SOPS file: {path.name}")

    try:
        completed = subprocess.run(
            ["sops", "--decrypt", "--output-type", "json", str(path)],
            check=False,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
    except OSError as error:
        raise ToolError("sops is not available") from error

    if completed.returncode != 0:
        raise ToolError(f"failed to decrypt {path.name}")

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ToolError(f"{path.name} did not decrypt to JSON") from error

    if not isinstance(payload, dict):
        raise ToolError(f"{path.name} did not decrypt to a JSON object")

    values: dict[str, str] = {}
    for key in required:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ToolError(f"{path.name} is missing {key}")
        values[key] = value
    return values
