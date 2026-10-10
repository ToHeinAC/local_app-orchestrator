"""Streamlit entry point: a directory of the local AI apps, one card each.

The orchestrator routes but never proxies: each card links straight to the app's
own service on its own port. It starts and stops nothing, so it is safe to
expose publicly. There is deliberately no exit button (see docs/ui.md).
"""

from __future__ import annotations

import streamlit as st

from src import status, theme
from src.config import load_config
from src.registry import RegistryError, load_apps

CFG = load_config()
COLUMNS = 2

TITLE = "KI-Anwendungen"
SUBTITLE = "Lokale BRENK-KI-Werkzeuge auf internem Server — wählen Sie eine Anwendung."
ONLINE = "🟢 Online"
ONLINE_LOCAL = "🟢 Online — nur im lokalen Netzwerk erreichbar"
OFFLINE = "⚪ Offline — Dienst läuft nicht"
OPEN = "Öffnen ↗"
REFRESH = "Status aktualisieren"
EMPTY = "Keine Anwendungen registriert. Tragen Sie eine in apps.toml ein."


def _card(app) -> None:
    """Render one app: icon, name, hint, status, and the Open button."""
    st_ = status.check(app, CFG.app_host, CFG.probe_timeout)
    with st.container(border=True):
        st.markdown(f"### {app.icon} {app.name}")
        st.caption(app.hint)
        if not st_.online:
            st.caption(OFFLINE)
        else:
            st.caption(ONLINE if st_.public else ONLINE_LOCAL)
        st.link_button(
            OPEN,
            st_.url,
            type="primary",
            disabled=not st_.online,
            use_container_width=True,
        )


def _grid(apps: list) -> None:
    """Lay the cards out in a fixed grid, one row at a time."""
    for row in range(0, len(apps), COLUMNS):
        for column, app in zip(st.columns(COLUMNS), apps[row : row + COLUMNS]):
            with column:
                _card(app)


def _sections(apps: list) -> dict[str, list]:
    """Group apps by their section, in order of first use; registry order within one."""
    groups: dict[str, list] = {}
    for app in apps:
        groups.setdefault(app.section, []).append(app)
    return groups


def main() -> None:
    st.set_page_config(
        page_title=TITLE,
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(theme.build_css(), unsafe_allow_html=True)

    st.title(TITLE)
    st.caption(SUBTITLE)

    try:
        apps = load_apps(CFG.apps_file)
    except RegistryError as exc:
        st.error(str(exc))
        st.stop()

    if not apps:
        st.markdown("---")
        st.info(EMPTY)
        return

    # One bordered panel per section, stacked; the cards inside form a two-column grid.
    for title, group in _sections(apps).items():
        with st.container(border=True):
            if title:
                st.markdown(f"## {title}")
            _grid(group)
    # Status is probed per page load; this just forces a fresh one.
    if st.button(REFRESH, key="refresh_btn"):
        st.rerun()


if __name__ == "__main__":
    main()
