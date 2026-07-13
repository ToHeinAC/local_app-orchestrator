"""Config defaults and environment overrides."""

from __future__ import annotations

from pathlib import Path

from src.config import load_config


def test_defaults(monkeypatch):
    for var in ("APP_PORT", "APP_HOST", "APPS_FILE", "PROBE_TIMEOUT"):
        monkeypatch.delenv(var, raising=False)
    cfg = load_config()
    # 8550 per PRD: avoids Streamlit's 8501 and the routed apps' 8520/8530.
    assert cfg.app_port == 8550
    assert cfg.app_host == "localhost"
    assert cfg.apps_file.name == "apps.toml"
    assert cfg.probe_timeout == 0.3


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("APP_PORT", "9001")
    monkeypatch.setenv("APP_HOST", "10.0.0.5")
    monkeypatch.setenv("APPS_FILE", "/etc/other.toml")
    monkeypatch.setenv("PROBE_TIMEOUT", "1.5")
    cfg = load_config()
    assert (cfg.app_port, cfg.app_host, cfg.probe_timeout) == (9001, "10.0.0.5", 1.5)
    assert cfg.apps_file == Path("/etc/other.toml")


def test_the_default_registry_path_is_absolute(monkeypatch):
    # Streamlit's cwd is not guaranteed, so the default must not be relative.
    monkeypatch.delenv("APPS_FILE", raising=False)
    assert load_config().apps_file.is_absolute()
