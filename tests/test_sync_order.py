from __future__ import annotations

from pathlib import Path

import pytest

from networking_vyos.errors import ToolError
from networking_vyos.pyinfra_runner import SYNC_STAGES, run_sync_stages, stage_names
from networking_vyos.verify import (
    require_pending_save,
    require_pending_save_known,
    verify_commands,
    verify_operational_state,
)


def test_sync_stages_are_separate_processes_in_contract_order() -> None:
    assert stage_names() == (
        "preflight",
        "assets",
        "footer",
        "commit",
        "auth",
        "verify",
        "save",
        "final",
    )
    assert [path.name for _, path in SYNC_STAGES] == [
        "preflight.py",
        "assets.py",
        "footer.py",
        "commit.py",
        "auth.py",
        "verify.py",
        "save.py",
        "final.py",
    ]


def test_run_sync_stages_invokes_each_deploy_file_once() -> None:
    seen: list[str] = []

    def runner(path: Path) -> None:
        seen.append(path.name)

    assert run_sync_stages(runner) == list(stage_names())
    assert seen == [path.name for _, path in SYNC_STAGES]


def test_failed_verification_never_reaches_save() -> None:
    seen: list[str] = []

    def runner(path: Path) -> None:
        seen.append(path.stem)
        if path.stem == "verify":
            raise ToolError("verification failed")

    with pytest.raises(ToolError, match="verification failed"):
        run_sync_stages(runner)
    assert seen == ["preflight", "assets", "footer", "commit", "auth", "verify"]
    assert "save" not in seen
    assert "final" not in seen


def test_pending_save_preflight_and_final_transitions() -> None:
    require_pending_save(False, expected=False, stage="preflight")
    require_pending_save(False, expected=False, stage="final check")
    with pytest.raises(ToolError, match="PendingSave is False"):
        require_pending_save(True, expected=False, stage="preflight")
    with pytest.raises(ToolError, match="PendingSave is False"):
        require_pending_save(None, expected=False, stage="final check")
    require_pending_save_known(False, stage="verification")
    require_pending_save_known(True, stage="verification")
    with pytest.raises(ToolError, match="could not determine PendingSave"):
        require_pending_save_known(None, stage="verification")


def test_verify_commands_require_accepted_state_and_reject_retired() -> None:
    commands = [
        "set system host-name 'gw01'",
        "set interfaces ethernet eth0 address '10.0.0.2/30'",
        "set interfaces bridge br10 address '10.10.10.1/24'",
        "set interfaces bridge br40 address '10.10.40.1/24'",
        "set interfaces bridge br70 address '10.10.70.1/24'",
        "set interfaces ethernet eth1 vif 10",
        "set interfaces ethernet eth1 vif 40",
        "set interfaces ethernet eth2 vif 10",
        "set interfaces ethernet eth2 vif 70",
        "set protocols static route 0.0.0.0/0 next-hop 10.0.0.1",
        "set service dhcp-server shared-network-name LAB_MGMT",
        "set container name tailscale environment TS_ROUTES value '10.10.0.0/16'",
        "set container name tailscale image docker.io/tailscale/tailscale:v1.96.5",
        "set container name coredns-glab-lol",
        "set firewall ipv4 forward filter default-action drop",
        "set firewall ipv4 input filter default-action drop",
        "set firewall ipv4 forward filter rule 100 inbound-interface name eth0",
        "set firewall ipv4 forward filter rule 100 jump-target WAN_FORWARD",
        "set firewall ipv4 forward filter rule 110 inbound-interface name br10",
        "set firewall ipv4 forward filter rule 110 jump-target MGMT_FORWARD",
        "set firewall ipv4 forward filter rule 120 inbound-interface name br40",
        "set firewall ipv4 forward filter rule 120 jump-target SANDBOX_FORWARD",
        "set firewall ipv4 forward filter rule 130 inbound-interface name br70",
        "set firewall ipv4 forward filter rule 130 jump-target OOB_FORWARD",
        "set firewall ipv4 input filter rule 100 inbound-interface name eth0",
        "set firewall ipv4 input filter rule 100 jump-target WAN_LOCAL",
        "set firewall ipv4 input filter rule 110 inbound-interface name br10",
        "set firewall ipv4 input filter rule 110 jump-target MGMT_LOCAL",
        "set firewall ipv4 input filter rule 120 inbound-interface name br40",
        "set firewall ipv4 input filter rule 120 jump-target SANDBOX_LOCAL",
        "set firewall ipv4 input filter rule 130 inbound-interface name br70",
        "set firewall ipv4 input filter rule 130 jump-target OOB_LOCAL",
    ]
    verify_commands(commands, stage="verification")
    with pytest.raises(ToolError, match="retired state"):
        verify_commands([*commands, "set protocols bgp system-as 64512"], stage="verification")
    with pytest.raises(ToolError, match="retired state"):
        verify_commands(
            [*commands, "set service dns forwarding listen-address 10.10.10.1"],
            stage="verification",
        )


def test_operational_verification_requires_routes_interfaces_and_containers() -> None:
    verify_operational_state(
        interfaces=(
            "eth0 10.0.0.2/30 up\n"
            "br10 10.10.10.1/24 up\n"
            "br40 10.10.40.1/24 up\n"
            "br70 10.10.70.1/24 up"
        ),
        routes="S>* 0.0.0.0/0 [1/0] via 10.0.0.1, eth0",
        containers="Up coredns-glab-lol\nUp tailscale",
        stage="verification",
    )
    with pytest.raises(ToolError, match="container is not running"):
        verify_operational_state(
            interfaces=(
                "eth0 10.0.0.2/30 up\n"
                "br10 10.10.10.1/24 up\n"
                "br40 10.10.40.1/24 up\n"
                "br70 10.10.70.1/24 up"
            ),
            routes="S>* 0.0.0.0/0 [1/0] via 10.0.0.1, eth0",
            containers="Exited coredns-glab-lol\nUp tailscale",
            stage="verification",
        )
