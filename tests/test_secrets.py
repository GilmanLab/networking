from __future__ import annotations

import json
from pathlib import Path

import pytest

from networking_vyos.errors import ToolError
from networking_vyos.secrets import load_password_hash, load_render_secrets


def test_decrypt_requires_json_object_and_expected_keys(
    secrets_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(_command, **_kwargs):  # type: ignore[no-untyped-def]
        stdout = json.dumps(
            {
                "public_key": "ssh-ed25519 AAAAPUBLIC vyos-gateway",
                "password_hash": "$6$hash",
            }
        )
        return type("Completed", (), {"returncode": 0, "stdout": stdout, "stderr": ""})()

    monkeypatch.setattr("networking_vyos.secrets.subprocess.run", fake_run)
    secrets = load_render_secrets()
    assert secrets.public_key == "AAAAPUBLIC"
    assert load_password_hash() == "$6$hash"


def test_invalid_render_values_are_rejected(
    secrets_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(_command, **_kwargs):  # type: ignore[no-untyped-def]
        stdout = json.dumps(
            {
                "public_key": "ssh-rsa AAAAPUBLIC",
                "password_hash": "$6$hash",
            }
        )
        return type("Completed", (), {"returncode": 0, "stdout": stdout, "stderr": ""})()

    monkeypatch.setattr("networking_vyos.secrets.subprocess.run", fake_run)
    with pytest.raises(ToolError, match="ssh-ed25519"):
        load_render_secrets()


def test_missing_password_hash_is_rejected_without_plaintext(
    secrets_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(_command, **_kwargs):  # type: ignore[no-untyped-def]
        stdout = json.dumps({"public_key": "ssh-ed25519 AAAAPUBLIC"})
        return type("Completed", (), {"returncode": 0, "stdout": stdout, "stderr": ""})()

    monkeypatch.setattr("networking_vyos.secrets.subprocess.run", fake_run)
    with pytest.raises(ToolError, match="password_hash") as error:
        load_password_hash()
    assert "secret" not in str(error.value)
    assert capsys.readouterr().out == ""
    assert secrets_root.is_dir()
