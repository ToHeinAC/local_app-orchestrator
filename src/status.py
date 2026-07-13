"""Where an app lives (URL) and whether it is up (port probe)."""

from __future__ import annotations

import socket
from dataclasses import dataclass

from src.registry import App


@dataclass(frozen=True)
class Status:
    online: bool
    url: str
    public: bool  # True when `url` is reachable from outside this machine


def _read_url_file(app: App) -> str | None:
    """Current public URL from the app's tunnel file, if it holds one.

    Absent/empty/unreadable is normal (the tunnel may be down), not an error —
    the caller falls back to the static `url`, then to host:port.
    """
    if app.url_file is None:
        return None
    try:
        url = app.url_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return url if url.startswith(("http://", "https://")) else None


def resolve(app: App, host: str) -> tuple[str, bool]:
    """Return (url, public). Precedence: url_file -> url -> http://host:port."""
    for url in (_read_url_file(app), app.url):
        if url:
            return url, True
    return f"http://{host}:{app.port}", False


def is_online(app: App, timeout: float) -> bool:
    """True when something accepts TCP connections on the app's port."""
    try:
        with socket.create_connection(("localhost", app.port), timeout=timeout):
            return True
    except OSError:
        return False


def check(app: App, host: str, timeout: float) -> Status:
    url, public = resolve(app, host)
    return Status(online=is_online(app, timeout), url=url, public=public)
