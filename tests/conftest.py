from __future__ import annotations

from pathlib import Path

import pytest

VALID_TEMPLATE = """\
/* The renderer MUST append the live footer copied from /config/config.boot. */
interfaces {
    ethernet eth0 {
        address 10.0.0.2/30
    }
    ethernet eth1 {
        vif 10 {
        }
        vif 40 {
        }
    }
    ethernet eth2 {
        vif 10 {
        }
        vif 70 {
        }
    }
}
interfaces {
    bridge br10 {
        address 10.10.10.1/24
    }
    bridge br40 {
        address 10.10.40.1/24
    }
    bridge br70 {
        address 10.10.70.1/24
    }
}
protocols {
    static {
        route 0.0.0.0/0 {
            next-hop 10.0.0.1 {
            }
        }
    }
}
service {
    dhcp-server {
    }
}
container {
    name tailscale {
    }
    name coredns-glab-lol {
    }
}
system {
    host-name gw01
    login {
        user vyos {
            authentication {
                public-keys operator {
                    key @@VYOS_PUBLIC_KEY@@
                    type ssh-ed25519
                }
            }
        }
    }
}
"""

LIVE_FOOTER = """\
// Warning: Do not remove the following line.
// vyos-config-version: "broadcast-relay@1:cluster@2"
// Release version: 1.5.0
"""


@pytest.fixture
def valid_template() -> str:
    return VALID_TEMPLATE


@pytest.fixture
def live_footer() -> str:
    return LIVE_FOOTER


@pytest.fixture
def repo_layout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, valid_template: str) -> Path:
    (tmp_path / "moon.yml").write_text("project: {}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    template = tmp_path / "vyos" / "gw01" / "config.boot.tmpl"
    template.parent.mkdir(parents=True)
    template.write_text(valid_template, encoding="utf-8")
    corefile = tmp_path / "vyos" / "gw01" / "assets" / "coredns" / "Corefile"
    corefile.parent.mkdir(parents=True)
    corefile.write_text("glab.lol:53 {}\n", encoding="utf-8")
    script = tmp_path / "vyos" / "gw01" / "assets" / "scripts" / "dns-mirror-fetch-glab-lol.sh"
    script.parent.mkdir(parents=True)
    script.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("NETWORKING_ROOT", str(tmp_path))
    return tmp_path


@pytest.fixture
def secrets_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "secrets"
    (root / "network" / "vyos").mkdir(parents=True)
    (root / "network" / "vyos" / "ssh.sops.yaml").write_text("sops: {}\n", encoding="utf-8")
    monkeypatch.setenv("GLAB_SECRETS_DIR", str(root))
    return root
