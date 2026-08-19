from __future__ import annotations

import pytest
from conftest import VALID_TEMPLATE

from networking_vyos.errors import ToolError
from networking_vyos.policy import validate_assets_present, validate_template


def test_valid_template_is_accepted() -> None:
    validate_template(VALID_TEMPLATE)


def test_tracked_template_satisfies_source_policy() -> None:
    from networking_vyos.render import load_template

    validate_template(load_template())
    validate_assets_present()


def test_rtr01_gateway_health_probe_is_allowed() -> None:
    from networking_vyos.render import load_template

    assert """rule 5 {
                action accept
                description "Allow rtr01 gateway health checks"
                protocol icmp
                source {
                    address 10.0.0.1
                }
            }""" in load_template()


def test_invented_footer_is_rejected() -> None:
    with pytest.raises(ToolError, match="must not invent"):
        validate_template(VALID_TEMPLATE + '\n// vyos-config-version: "guessed@1"\n')


@pytest.mark.parametrize(
    ("needle", "label"),
    [
        ("@@VYOS_PUBLIC_KEY@@", "@@VYOS_PUBLIC_KEY@@"),
        ("host-name gw01", "hostname gw01"),
        ("/config/config.boot", "live footer source policy"),
    ],
)
def test_missing_required_policy_is_rejected(needle: str, label: str) -> None:
    with pytest.raises(ToolError, match=label):
        validate_template(VALID_TEMPLATE.replace(needle, "removed"))


@pytest.mark.parametrize(
    ("retired", "label"),
    [
        ("vif 20 {\n        }\n", "VLAN20"),
        ("name tinkerbell {\n        }\n", "Tinkerbell"),
        ("name pdns-auth {\n        }\n", "PowerDNS"),
        ("domain lab.gilman.io {\n        }\n", "lab.gilman.io"),
        ("name incusos-artifacts {\n        }\n", "artifact serving"),
        ("name bootstrap-k0s {\n        }\n", "bootstrap-k0s"),
        ("bgp {\n        }\n", "BGP"),
        ("bridge br20 {\n        }\n", "UM760 bridge"),
        ("host-name gateway\n", "hostname gateway"),
    ],
)
def test_retired_state_is_rejected(retired: str, label: str) -> None:
    with pytest.raises(ToolError, match=label):
        validate_template(VALID_TEMPLATE + retired)


def test_missing_assets_are_rejected(tmp_path, monkeypatch) -> None:
    (tmp_path / "moon.yml").write_text("project: {}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    monkeypatch.setenv("NETWORKING_ROOT", str(tmp_path))
    with pytest.raises(ToolError, match="missing nonsecret asset"):
        validate_assets_present()
