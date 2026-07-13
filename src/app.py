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
SUBTITLE = "Lokale KI-Werkzeuge auf diesem Server — wählen Sie eine Anwendung."
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
    st.markdown("---")

    try:
        apps = load_apps(CFG.apps_file)
    except RegistryError as exc:
        st.error(str(exc))
        st.stop()

    if not apps:
        st.info(EMPTY)
        return

    _grid(apps)
    st.markdown("---")
    # Status is probed per page load; this just forces a fresh one.
    if st.button(REFRESH, key="refresh_btn"):
        st.rerun()


if __name__ == "__main__":
    main()
