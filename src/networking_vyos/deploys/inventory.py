"""Static single-host inventory for gw01."""

from __future__ import annotations

from networking_vyos.config import connection_from_sources

_connection = connection_from_sources()

hosts = [
    (
        "gw01",
        _connection.pyinfra_data(),
    )
]
