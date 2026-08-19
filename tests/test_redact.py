from __future__ import annotations

from networking_vyos.redact import sanitize_fact_commands


def test_sanitize_masks_quoted_and_unquoted_ts_authkey_values() -> None:
    commands = [
        "set container name tailscale environment TS_AUTHKEY value 'tskey-client-secret?ephemeral=false'",
        'set container name tailscale environment TS_AUTHKEY value "tskey-client-secret"',
        "set container name tailscale environment ts_authkey value tskey-client-UNQUOTED",
        "set system host-name 'gw01'",
        "set interfaces bridge br10 address '10.10.10.1/24'",
    ]
    sanitized = sanitize_fact_commands(commands)
    joined = "\n".join(sanitized)
    assert "tskey-client-secret" not in joined
    assert "tskey-client-UNQUOTED" not in joined
    assert sanitized[0].endswith("value '****************'")
    assert sanitized[1].endswith('value "****************"')
    assert sanitized[2].endswith("value ****************")
    assert (
        sanitize_fact_commands(
            ["set system login user vyos authentication encrypted-password '$6$salt$digest'"]
        )[0]
        == "set system login user vyos authentication encrypted-password '****************'"
    )
    assert sanitized[3] == "set system host-name 'gw01'"
    assert sanitized[4] == "set interfaces bridge br10 address '10.10.10.1/24'"


def test_sanitize_never_emits_secret_bearing_ts_authkey_lines() -> None:
    leaked = [
        "set container name tailscale environment TS_AUTHKEY value tskey-client-AAAAAAAAAAAAAAAAAAAAAAAA",
        "set container name tailscale environment Ts_AuthKey value 'tskey-client-BBBB'",
        'SET CONTAINER NAME tailscale ENVIRONMENT TS_AUTHKEY VALUE "tskey-client-CCCC"',
    ]
    sanitized = sanitize_fact_commands(leaked)
    for line in sanitized:
        assert "tskey-" not in line.lower()
        assert "****************" in line
        assert "TS_AUTHKEY" in line.upper()
