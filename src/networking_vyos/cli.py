"""Argparse operator surface for validate, facts, and sync."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from networking_vyos.config import apply_connection_env, connection_from_sources
from networking_vyos.errors import ToolError
from networking_vyos.lock import exclusive_gw01_lock
from networking_vyos.policy import validate_assets_present, validate_template
from networking_vyos.pyinfra_runner import collect_facts, run_sync_stages
from networking_vyos.redact import sanitize_fact_commands
from networking_vyos.render import load_template
from networking_vyos.secrets import load_password_hash, load_render_secrets


def _connection_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--host", help="Override VYOS_HOST")
    parent.add_argument("--ssh-user", help="Override VYOS_SSH_USER")
    parent.add_argument("--ssh-key", help="Override VYOS_SSH_KEY")
    parent.add_argument("--known-hosts", help="Override VYOS_KNOWN_HOSTS")
    return parent


def build_parser() -> argparse.ArgumentParser:
    parent = _connection_parser()
    parser = argparse.ArgumentParser(
        prog="networking_vyos",
        description="Validate, inspect, and sync the lab2 gw01 VyOS gateway.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "validate",
        parents=[parent],
        help="Validate the tracked template and nonsecret assets",
    )

    facts = sub.add_parser(
        "facts",
        parents=[parent],
        help="Collect Version, redacted commands, and PendingSave",
    )
    facts.add_argument("--json", action="store_true", help="Emit machine-readable JSON on stdout")

    sync = sub.add_parser("sync", parents=[parent], help="Commit, verify, then save gw01")
    sync.add_argument("--yes", action="store_true", help="Skip the TTY confirmation prompt")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        connection = connection_from_sources(
            host=args.host,
            ssh_user=args.ssh_user,
            ssh_key=args.ssh_key,
            known_hosts=args.known_hosts,
        )
        apply_connection_env(connection)
        if args.command == "validate":
            return cmd_validate()
        if args.command == "facts":
            return cmd_facts(as_json=args.json)
        if args.command == "sync":
            return cmd_sync(yes=args.yes)
        raise ToolError(f"unknown command {args.command}")
    except ToolError as error:
        print(str(error), file=sys.stderr)
        return 1


def cmd_validate() -> int:
    validate_template(load_template())
    validate_assets_present()
    print("gw01 template and nonsecret assets are valid", file=sys.stderr)
    return 0


def cmd_facts(*, as_json: bool) -> int:
    payload = collect_facts()
    commands = payload.get("commands")
    if isinstance(commands, list):
        payload = {**payload, "commands": sanitize_fact_commands(commands)}
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    version = payload.get("version")
    version_label = ""
    if isinstance(version, dict):
        version_label = str(version.get("version", ""))
    sanitized = payload.get("commands")
    command_count = len(sanitized) if isinstance(sanitized, list) else 0
    print(f"version: {version_label or 'unknown'}", file=sys.stderr)
    print(f"pending_save: {payload.get('pending_save')!r}", file=sys.stderr)
    print(f"commands: {command_count} redacted lines", file=sys.stderr)
    return 0


def cmd_sync(*, yes: bool) -> int:
    if not yes and not sys.stdin.isatty():
        raise ToolError("refusing non-TTY sync without --yes")
    if not yes:
        print(
            "Apply unsaved gw01 configuration, then save after verification? [y/N]",
            file=sys.stderr,
        )
        answer = input().strip().lower()
        if answer not in {"y", "yes"}:
            raise ToolError("sync cancelled")

    validate_template(load_template())
    validate_assets_present()
    load_render_secrets()
    load_password_hash()

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as handle:
        footer_path = Path(handle.name)
    os.environ["NETWORKING_FOOTER_PATH"] = str(footer_path)
    try:
        with exclusive_gw01_lock():
            for name in run_sync_stages():
                print(f"completed {name}", file=sys.stderr)
    finally:
        footer_path.unlink(missing_ok=True)
    print("gw01 sync complete", file=sys.stderr)
    return 0
