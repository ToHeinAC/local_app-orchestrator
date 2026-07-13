"""Environment/config loading.

Scalars live in the environment (python-dotenv); the *list of apps* lives in
apps.toml — a list of records is awkward to encode in env vars. See registry.py.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    app_port: int
    app_host: str
    apps_file: Path
    probe_timeout: float


def load_config() -> Config:
    """Read config from the environment, applying sensible defaults."""
    return Config(
        app_port=int(os.getenv("APP_PORT", "8550")),
        # Host used to build the fallback URL for apps without a public URL.
        app_host=os.getenv("APP_HOST", "localhost"),
        apps_file=Path(os.getenv("APPS_FILE", str(ROOT / "apps.toml"))),
        # Kept short: every app is probed on each page load.
        probe_timeout=float(os.getenv("PROBE_TIMEOUT", "0.3")),
    )
