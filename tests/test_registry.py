"""apps.toml parsing and validation. A bad registry must fail loudly, naming
the culprit — a silently dropped app is a link the user never sees."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.registry import RegistryError, load_apps

ROOT = Path(__file__).resolve().parent.parent


def _write(tmp_path, body: str) -> Path:
    path = tmp_path / "apps.toml"
    path.write_text(body, encoding="utf-8")
    return path


def test_loads_every_field(apps_file):
    wiki, summary = load_apps(apps_file)
    assert (wiki.name, wiki.hint, wiki.icon, wiki.port) == ("Wiki", "lokales Wiki", "📚", 8520)
    assert wiki.url is None and wiki.url_file is None
    assert summary.url == "https://static.example.com/"


def test_url_file_becomes_a_path(tmp_path):
    path = _write(
        tmp_path,
        '[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport=8520\nurl_file="/tmp/w.txt"\n',
    )
    assert load_apps(path)[0].url_file == Path("/tmp/w.txt")


def test_empty_registry_is_valid(tmp_path):
    # An empty file is not an error: the app shows "nothing registered yet".
    assert load_apps(_write(tmp_path, "")) == []


@pytest.mark.parametrize("field", ["name", "hint", "icon", "port"])
def test_missing_required_field_is_rejected(tmp_path, field):
    entry = {"name": '"W"', "hint": '"h"', "icon": '"📚"', "port": "8520"}
    del entry[field]
    body = "[[apps]]\n" + "".join(f"{k}={v}\n" for k, v in entry.items())
    with pytest.raises(RegistryError, match=field):
        load_apps(_write(tmp_path, body))


@pytest.mark.parametrize("port", ["0", "70000", '"8520"'])
def test_invalid_port_is_rejected(tmp_path, port):
    body = f'[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport={port}\n'
    with pytest.raises(RegistryError, match="invalid port"):
        load_apps(_write(tmp_path, body))


def test_duplicate_ports_are_rejected(tmp_path):
    # Two cards on one port would probe and link to the same service.
    body = (
        '[[apps]]\nname="A"\nhint="h"\nicon="📚"\nport=8520\n'
        '[[apps]]\nname="B"\nhint="h"\nicon="🔎"\nport=8520\n'
    )
    with pytest.raises(RegistryError, match="8520.*'A'.*'B'"):
        load_apps(_write(tmp_path, body))


def test_unknown_field_is_rejected(tmp_path):
    # Catches typos like `urlfile =` that would otherwise be silently ignored.
    body = '[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport=8520\nurlfile="/tmp/w.txt"\n'
    with pytest.raises(RegistryError, match="urlfile"):
        load_apps(_write(tmp_path, body))


def test_malformed_toml_is_rejected(tmp_path):
    with pytest.raises(RegistryError, match="not valid TOML"):
        load_apps(_write(tmp_path, "[[apps]\nname=="))


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(RegistryError, match="not found"):
        load_apps(tmp_path / "nope.toml")


def test_the_shipped_registry_is_valid():
    # The real apps.toml must parse — a broken one breaks the whole page.
    apps = load_apps(ROOT / "apps.toml")
    assert {a.port for a in apps} == {8511, 8520, 8530, 8560}
    by_section = {s: [a.name for a in apps if a.section == s] for s in {a.section for a in apps}}
    assert by_section == {
        "Wissensmanagement": ["KI-WissensWiki", "BrAIn"],
        "Services": ["KI-Zusammenfassung", "KI-Übersetzer"],
    }


def test_section_defaults_to_empty(apps_file):
    assert {a.section for a in load_apps(apps_file)} == {""}


def test_section_must_be_a_string(tmp_path):
    body = '[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport=8520\nsection=1\n'
    with pytest.raises(RegistryError, match="section must be"):
        load_apps(_write(tmp_path, body))
