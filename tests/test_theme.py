"""The Forest theme. Ported from local_summarizer, so the invariants that
protect it there protect it here too."""

from __future__ import annotations

from src import theme


def test_css_is_a_style_block():
    css = theme.build_css().strip()
    assert css.startswith("<style>") and css.endswith("</style>")


def test_every_palette_value_is_used():
    css = theme.build_css()
    for key, value in theme.FOREST.items():
        assert value in css, f"palette key '{key}' is never applied"


def test_both_fonts_are_imported():
    css = theme.build_css()
    assert "Inter" in css and "Libre+Baskerville" in css


def test_material_icon_ligatures_are_guarded():
    # Setting font-family on `.stApp *` would render icons as literal text.
    css = theme.build_css()
    assert "font-family" not in css.split(".stApp, .stApp *")[1].split("}")[0]
    assert "Material Symbols Rounded" in css


def test_primary_link_button_label_stays_white():
    # `.stApp *` paints the nested <p> dark unless descendants are re-asserted.
    assert '.stLinkButton > a[kind="primary"] *' in theme.build_css()


def test_disabled_link_button_is_not_clickable():
    # An offline app's button must not navigate anywhere.
    css = theme.build_css()
    assert "pointer-events: none" in css.split('a[disabled]')[-1]


def test_cards_in_a_row_are_equal_height():
    # A longer hint wraps to more lines; without stretch the neighbour card is
    # left stunted and the Open buttons no longer line up.
    css = theme.build_css()
    assert "align-items: stretch" in css
    assert "margin-top: auto" in css  # pushes the Open button to the card's foot


def test_a_custom_palette_overrides():
    css = theme.build_css({**theme.FOREST, "primary": "#ff0000"})
    assert "#ff0000" in css and "#234637" not in css
