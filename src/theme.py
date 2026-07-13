"""Forest theme: palette + injectable CSS.

Ported from ToHeinAC/local_summarizer (Apache-2.0) so both apps share a look.
Colors mirror ``.streamlit/config.toml``; the CSS below re-asserts them because
Streamlit's config alone does not reach every widget.

Trimmed to the widgets this app actually uses: link buttons (the Open action),
bordered containers (the app cards), captions and headings. The summarizer's
uploader/download/progress rules are intentionally absent, as is its
``sidebar_bg`` — this app has no sidebar. ``config.toml`` still carries
``secondaryBackgroundColor``, which Streamlit's own shell uses.
"""

from __future__ import annotations

FOREST = {
    "bg": "#f6f7f2",
    "widget_bg": "#ffffff",
    "text": "#1a1f1c",
    "text_muted": "#5a6b5e",
    "primary": "#234637",
    "border": "#d4dbd6",
    "hover": "rgba(35,70,55,0.10)",
    "offline": "#9aa8a0",
}

_FONTS = (
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600"
    "&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap"
)


def build_css(t: dict = FOREST) -> str:
    """Return the ``<style>`` block for the given palette."""
    return f"""
    <style>
    @import url('{_FONTS}');

    html, body {{
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 15px;
    }}
    /* Catch ALL elements' color — overrides Streamlit's inline textColor from
       config.toml. Do NOT set font-family here: it breaks icon ligatures. */
    .stApp, .stApp * {{
        color: {t['text']} !important;
    }}
    [data-testid="stIconMaterial"],
    span.material-icons,
    span.material-icons-outlined,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [class*="material-symbols"] {{
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }}

    .stApp {{ background-color: {t['bg']} !important; }}
    [data-testid="block-container"],
    [data-testid="stVerticalBlock"],
    section.main > div {{
        background-color: {t['bg']} !important;
    }}

    h1, h2, h3 {{
        font-family: 'Libre Baskerville', Georgia, serif !important;
        font-weight: 700;
    }}
    h1 {{ font-size: 1.75rem; margin-bottom: 0.25rem; }}

    /* Link buttons are this app's primary action (Open). Streamlit renders them
       as <a>, so they need their own rules — .stButton does not reach them. */
    .stLinkButton > a {{
        border-radius: 6px !important;
        font-weight: 500 !important;
        text-transform: none !important;
        font-size: 0.875rem !important;
        border: 1px solid {t['border']} !important;
        background-color: {t['widget_bg']} !important;
        transition: background-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .stLinkButton > a:hover {{
        background-color: {t['hover']} !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.15) !important;
    }}
    .stLinkButton > a[kind="primary"],
    .stLinkButton > a[kind="primary"]:hover {{
        background-color: {t['primary']} !important;
        border-color: {t['primary']} !important;
    }}
    /* The label lives in a nested <p>, which `.stApp *` would paint dark. */
    .stLinkButton > a[kind="primary"],
    .stLinkButton > a[kind="primary"] * {{
        color: #ffffff !important;
    }}
    /* A disabled link button marks an offline app: mute it, kill the pointer. */
    .stLinkButton > a[disabled],
    .stLinkButton > a[disabled] * {{
        color: {t['offline']} !important;
        background-color: {t['bg']} !important;
        border-color: {t['border']} !important;
        cursor: not-allowed !important;
        pointer-events: none !important;
    }}

    /* App cards */
    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        border-color: {t['border']} !important;
        background-color: {t['widget_bg']} !important;
    }}

    /* Equal card heights: a longer hint wraps to more lines, which would
       otherwise leave the shorter card stunted next to it. Stretch every card
       in a row to the tallest one, then push the Open button to the bottom so
       the buttons line up. Height, not a fixed px value — the text decides. */
    [data-testid="stHorizontalBlock"] {{ align-items: stretch !important; }}
    [data-testid="stColumn"],
    [data-testid="stColumn"] > div,
    [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] > div {{
        height: 100% !important;
    }}
    [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] > div {{
        display: flex !important;
        flex-direction: column !important;
    }}
    [data-testid="stColumn"] .stLinkButton {{ margin-top: auto !important; }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {{ color: {t['text_muted']} !important; }}

    [data-testid="stAlert"], [data-testid="stAlert"] * {{ color: {t['text']} !important; }}

    hr {{ border: none; border-top: 1px solid {t['border']}; margin: 1.25rem 0; }}

    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
    </style>
    """
