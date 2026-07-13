"""URL resolution and the liveness probe.

The precedence rules matter: a stale hard-coded URL is a dead link, and a
localhost fallback handed to a remote visitor resolves to *their* machine.
"""

from __future__ import annotations

import dataclasses

from src import status
from src.registry import App


def _app(**over) -> App:
    base = dict(name="Wiki", hint="h", icon="📚", port=8520)
    return App(**{**base, **over})


def test_url_file_wins_over_static_url(tmp_path):
    # Quick-tunnel URLs rotate; the file holds the current one, so it must win.
    f = tmp_path / "url.txt"
    f.write_text("https://fresh.trycloudflare.com\n")
    app = _app(url="https://stale.trycloudflare.com", url_file=f)
    assert status.resolve(app, "localhost") == ("https://fresh.trycloudflare.com", True)


def test_static_url_used_when_no_url_file():
    app = _app(url="https://static.example.com/")
    assert status.resolve(app, "localhost") == ("https://static.example.com/", True)


def test_falls_back_to_host_and_port():
    # Not public: this URL only works from the server / LAN.
    assert status.resolve(_app(), "localhost") == ("http://localhost:8520", False)


def test_fallback_honours_the_configured_host():
    assert status.resolve(_app(), "10.0.0.5")[0] == "http://10.0.0.5:8520"


def test_missing_url_file_falls_through_to_static_url(tmp_path):
    # A down tunnel deletes its URL file. That is normal, not an error.
    app = _app(url="https://static.example.com/", url_file=tmp_path / "gone.txt")
    assert status.resolve(app, "localhost") == ("https://static.example.com/", True)


def test_empty_url_file_falls_through(tmp_path):
    f = tmp_path / "url.txt"
    f.write_text("   \n")
    assert status.resolve(_app(url_file=f), "localhost") == ("http://localhost:8520", False)


def test_garbage_url_file_falls_through(tmp_path):
    # Guards against linking the browser to a log line or an error message.
    f = tmp_path / "url.txt"
    f.write_text("ERROR: tunnel failed to start")
    assert status.resolve(_app(url_file=f), "localhost") == ("http://localhost:8520", False)


def test_online_when_something_listens(open_port):
    assert status.is_online(_app(port=open_port), timeout=1.0) is True


def test_offline_when_nothing_listens(closed_port):
    assert status.is_online(_app(port=closed_port), timeout=1.0) is False


def test_check_combines_liveness_and_url(open_port, tmp_path):
    f = tmp_path / "url.txt"
    f.write_text("https://fresh.trycloudflare.com")
    got = status.check(_app(port=open_port, url_file=f), "localhost", timeout=1.0)
    assert dataclasses.astuple(got) == (True, "https://fresh.trycloudflare.com", True)
