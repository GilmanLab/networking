"""Controller-side masking for operator-facing facts output."""

from __future__ import annotations

import re
from collections.abc import Iterable

_TS_AUTHKEY = re.compile(r"TS_AUTHKEY", re.IGNORECASE)
_ENCRYPTED_PASSWORD = re.compile(r"\bencrypted-password\b", re.IGNORECASE)
_VALUE = re.compile(
    r'(?P<prefix>\bvalue\s+)(?P<quote>["\']?)(?P<body>.*?)(?P=quote)\s*$',
    re.IGNORECASE,
)
_PASSWORD_VALUE = re.compile(
    r'(?P<prefix>\bencrypted-password\s+)(?P<quote>["\']?)(?P<body>.*?)(?P=quote)\s*$',
    re.IGNORECASE,
)
_MASK = "****************"


def sanitize_fact_commands(commands: Iterable[object]) -> list[str]:
    """Mask secret-bearing configuration values before operator emission."""

    sanitized: list[str] = []
    for command in commands:
        line = str(command)
        if _TS_AUTHKEY.search(line):
            line = _mask_ts_authkey_line(line)
        if _ENCRYPTED_PASSWORD.search(line):
            line = _mask_encrypted_password_line(line)
        sanitized.append(line)
    return sanitized


def _mask_ts_authkey_line(line: str) -> str:
    masked, count = _VALUE.subn(rf"\g<prefix>\g<quote>{_MASK}\g<quote>", line)
    if count:
        return masked
    return _TS_AUTHKEY.sub("TS_AUTHKEY", line, count=1) + f" {_MASK}"


def _mask_encrypted_password_line(line: str) -> str:
    masked, count = _PASSWORD_VALUE.subn(rf"\g<prefix>\g<quote>{_MASK}\g<quote>", line)
    if count:
        return masked
    return _ENCRYPTED_PASSWORD.sub("encrypted-password", line, count=1) + f" {_MASK}"
