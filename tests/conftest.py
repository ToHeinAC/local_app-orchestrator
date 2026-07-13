"""Shared fixtures. Every test runs offline: no tunnels, no real apps."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from src.registry import App


@pytest.fixture
def apps_file(tmp_path) -> Path:
    """A minimal, valid two-app registry."""
    path = tmp_path / "apps.toml"
    path.write_text(
        """
[[apps]]
name = "Wiki"
hint = "lokales Wiki"
icon = "📚"
port = 8520

[[apps]]
name = "Zusammenfassung"
hint = "lokales Tool"
icon = "🔎"
port = 8530
url = "https://static.example.com/"
""",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def app() -> App:
    """One app with no public URL configured."""
    return App(name="Wiki", hint="lokales Wiki", icon="📚", port=8520)


@pytest.fixture
def open_port():
    """A really-listening socket, so is_online() has something true to find."""
    sock = socket.socket()
    sock.bind(("localhost", 0))  # port 0 -> the OS picks a free one
    sock.listen(1)
    yield sock.getsockname()[1]
    sock.close()


@pytest.fixture
def closed_port() -> int:
    """A port nothing listens on: bound to claim it, then released."""
    sock = socket.socket()
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port
