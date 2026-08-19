from __future__ import annotations

import json
from pathlib import Path

import pytest

from networking_vyos import cli
from networking_vyos.errors import ToolError


def test_facts_json_keeps_stdout_machine_clean(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    payload = {
        "pending_save": False,
        "version": {"version": "1.5"},
        "commands": ["set system host-name gw01"],
    }
    monkeypatch.setattr(cli, "collect_facts", lambda: payload)
    assert cli.main(["facts", "--json"]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == payload


def test_facts_json_masks_ts_authkey_before_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "collect_facts",
        lambda: {
            "pending_save": False,
            "version": {"version": "1.5"},
            "commands": [
                "set system host-name 'gw01'",
                "set container name tailscale environment TS_AUTHKEY value 'tskey-client-secret'",
            ],
        },
    )
    assert cli.main(["facts", "--json"]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    payload = json.loads(captured.out)
    joined = "\n".join(payload["commands"])
    assert "tskey-client-secret" not in joined
    assert "tskey-" not in joined
    assert "****************" in joined
    assert payload["commands"][0] == "set system host-name 'gw01'"


def test_facts_human_output_stays_on_stderr(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "collect_facts",
        lambda: {"pending_save": False, "version": {"version": "1.5"}, "commands": []},
    )
    assert cli.main(["facts"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "version: 1.5" in captured.err
    assert "pending_save: False" in captured.err


def test_sync_without_yes_on_non_tty_is_refused(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    assert cli.main(["sync"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "refusing non-TTY sync without --yes" in captured.err


def test_sync_yes_skips_prompt(
    monkeypatch: pytest.MonkeyPatch,
    repo_layout: Path,
    secrets_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli, "load_render_secrets", lambda: object())
    monkeypatch.setattr(cli, "load_password_hash", lambda: "$6$hash")
    monkeypatch.setattr(
        cli,
        "run_sync_stages",
        lambda: ["preflight", "assets", "footer", "commit", "auth", "verify", "save", "final"],
    )
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    assert cli.main(["sync", "--yes"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "completed preflight" in captured.err
    assert "gw01 sync complete" in captured.err
    assert secrets_root.is_dir()
    assert repo_layout.is_dir()


def test_connection_flags_override_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VYOS_HOST", "10.9.9.9")
    monkeypatch.setenv("VYOS_SSH_USER", "env-user")
    import os

    monkeypatch.setattr(cli, "cmd_validate", lambda: 0)
    assert cli.main(["validate", "--host", "10.1.1.1", "--ssh-user", "flag-user"]) == 0
    assert os.environ["VYOS_HOST"] == "10.1.1.1"
    assert os.environ["VYOS_SSH_USER"] == "flag-user"


def test_tool_errors_do_not_print_secret_values(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "cmd_validate",
        lambda: (_ for _ in ()).throw(ToolError("failed to decrypt ssh.sops.yaml")),
    )
    assert cli.main(["validate"]) == 1
    captured = capsys.readouterr()
    assert "failed to decrypt ssh.sops.yaml" in captured.err
    assert "tskey-" not in captured.err
    assert "$6$" not in captured.err
