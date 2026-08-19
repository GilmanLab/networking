"""Apply the console password hash after the secret-free full config load."""

from __future__ import annotations

from pyinfra_vyos import config

from networking_vyos.secrets import load_password_hash

config(
    name="Apply the vyos console password hash without saving",
    path=["system", "login", "user", "vyos", "authentication"],
    values={"encrypted-password": load_password_hash()},
    save=False,
)
