"""App registry: parse apps.toml into validated App records."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

REQUIRED = ("name", "hint", "icon", "port")


class RegistryError(ValueError):
    """apps.toml is missing, malformed, or holds an invalid app entry."""


@dataclass(frozen=True)
class App:
    name: str
    hint: str
    icon: str
    port: int
    url: str | None = None
    url_file: Path | None = None
    featured: bool = False  # full-width card above the grid


def _build(entry: dict, index: int) -> App:
    """Validate one [[apps]] block. `index` is only used for error messages."""
    where = f"apps.toml entry #{index}"
    missing = [f for f in REQUIRED if entry.get(f) in (None, "")]
    if missing:
        raise RegistryError(f"{where} is missing required field(s): {', '.join(missing)}")

    unknown = set(entry) - set(REQUIRED) - {"url", "url_file", "featured"}
    if unknown:
        raise RegistryError(f"{where} ({entry['name']}) has unknown field(s): {', '.join(sorted(unknown))}")

    port = entry["port"]
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise RegistryError(f"{where} ({entry['name']}) has an invalid port: {port!r}")

    featured = entry.get("featured", False)
    if not isinstance(featured, bool):
        raise RegistryError(f"{where} ({entry['name']}): featured must be true or false")

    url_file = entry.get("url_file")
    return App(
        name=entry["name"],
        hint=entry["hint"],
        icon=entry["icon"],
        port=port,
        url=entry.get("url"),
        url_file=Path(url_file) if url_file else None,
        featured=featured,
    )


def load_apps(path: Path) -> list[App]:
    """Parse apps.toml. Raises RegistryError with a message naming the culprit."""
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryError(f"App registry not found: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise RegistryError(f"App registry {path} is not valid TOML: {exc}") from exc

    apps = [_build(entry, i) for i, entry in enumerate(raw.get("apps", []), start=1)]

    # A duplicate port means two cards would probe and link to the same service.
    seen: dict[int, str] = {}
    for app in apps:
        if app.port in seen:
            raise RegistryError(
                f"apps.toml: port {app.port} is used by both '{seen[app.port]}' and '{app.name}'"
            )
        seen[app.port] = app.name

    return apps
