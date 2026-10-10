"""The page, driven end-to-end through Streamlit's AppTest.

Ports are real but ephemeral (see conftest), so status is deterministic and no
test depends on an app actually running on 8520/8530.
"""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

APP_FILE = "src/app.py"


def _links(at):
    """link_button has no AppTest accessor; .get() exposes the raw proto."""
    return [e.proto for e in at.get("link_button")]


@pytest.fixture
def registry(tmp_path, monkeypatch, open_port, closed_port):
    """One online app with a public URL, one offline app without."""
    path = tmp_path / "apps.toml"
    path.write_text(
        f"""
[[apps]]
name = "KI-WissensWiki"
hint = "lokales KI-Wissensmanagement-Wiki"
icon = "📚"
port = {open_port}
url = "https://wiki.trycloudflare.com/"

[[apps]]
name = "KI-Zusammenfassung"
hint = "lokales KI-Zusammenfassungstool"
icon = "🔎"
port = {closed_port}
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("APPS_FILE", str(path))
    return path


@pytest.fixture
def at(registry):
    return AppTest.from_file(APP_FILE).run()


def test_one_card_per_registered_app(at):
    assert len(_links(at)) == 2


def test_name_icon_and_hint_are_rendered(at):
    body = " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)
    assert "📚 KI-WissensWiki" in body
    assert "lokales KI-Wissensmanagement-Wiki" in body


def test_online_app_links_to_its_public_url(at):
    wiki = _links(at)[0]
    assert wiki.url == "https://wiki.trycloudflare.com/"
    assert wiki.disabled is False


def test_offline_app_button_is_disabled(at):
    assert _links(at)[1].disabled is True


def test_offline_app_is_marked_offline(at):
    assert any("Offline" in c.value for c in at.caption)


def test_app_without_a_public_url_is_marked_local_only(registry, open_port, monkeypatch):
    # No url/url_file -> the localhost fallback, which a remote visitor cannot use.
    registry.write_text(
        f'[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport={open_port}\n', encoding="utf-8"
    )
    at = AppTest.from_file(APP_FILE).run()
    assert _links(at)[0].url == f"http://localhost:{open_port}"
    assert any("nur im lokalen Netzwerk" in c.value for c in at.caption)


def test_url_file_beats_the_static_url(registry, tmp_path, open_port):
    fresh = tmp_path / "url.txt"
    fresh.write_text("https://fresh.trycloudflare.com")
    registry.write_text(
        f'[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport={open_port}\n'
        f'url="https://stale.example.com/"\nurl_file="{fresh}"\n',
        encoding="utf-8",
    )
    at = AppTest.from_file(APP_FILE).run()
    assert _links(at)[0].url == "https://fresh.trycloudflare.com"


def test_a_broken_registry_shows_an_error_and_stops(registry):
    registry.write_text('[[apps]]\nname="W"\nhint="h"\nicon="📚"\nport=0\n', encoding="utf-8")
    at = AppTest.from_file(APP_FILE).run()
    assert "invalid port" in at.error[0].value
    assert not _links(at)  # stopped before rendering any card


def test_an_empty_registry_explains_itself(registry):
    registry.write_text("", encoding="utf-8")
    at = AppTest.from_file(APP_FILE).run()
    assert "apps.toml" in at.info[0].value
    assert not _links(at)


def test_apps_are_grouped_into_sections_in_registry_order(registry, open_port, closed_port):
    # Sections appear in order of first use; apps keep their registry order inside one.
    registry.write_text(
        f'[[apps]]\nname="A"\nhint="h"\nicon="📚"\nport={open_port}\nsection="Oben"\n'
        f'[[apps]]\nname="B"\nhint="h"\nicon="🔎"\nport={closed_port}\nsection="Unten"\n'
        f'url="https://b.example.com/"\n'
        f'[[apps]]\nname="C"\nhint="h"\nicon="🧠"\nport={open_port + 1}\nsection="Oben"\n',
        encoding="utf-8",
    )
    at = AppTest.from_file(APP_FILE).run()
    headings = [m.value for m in at.markdown if m.value.startswith("## ")]
    assert headings == ["## Oben", "## Unten"]
    names = [m.value for m in at.markdown if m.value.startswith("### ")]
    assert names == ["### 📚 A", "### 🧠 C", "### 🔎 B"]


def test_refresh_reruns_without_error(at):
    at.button[0].click().run()
    assert not at.exception


def test_there_is_no_exit_button(at):
    # Deliberate: the orchestrator kills no process, its own included.
    labels = [b.label.lower() for b in at.button]
    assert not any(word in label for label in labels for word in ("beenden", "exit", "stop"))
