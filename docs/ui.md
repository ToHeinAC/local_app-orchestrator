# UI

## Forest theme

Ported from [local_summarizer](https://github.com/ToHeinAC/local_summarizer)
(Apache-2.0, same author) so the apps look like one family.

```python
FOREST = {
    "bg":         "#f6f7f2",   # page background
    "widget_bg":  "#ffffff",   # cards, buttons
    "text":       "#1a1f1c",
    "text_muted": "#5a6b5e",   # hints, status captions
    "primary":    "#234637",   # Open button
    "border":     "#d4dbd6",
    "hover":      "rgba(35,70,55,0.10)",
    "offline":    "#9aa8a0",   # disabled Open button
}
```

Fonts: **Inter** (400/500/600) for body at 15px, **Libre Baskerville** 700 for
headings, both via a single Google Fonts `@import` inside the injected `<style>`
block. Offline, they degrade to `system-ui` / `Georgia`. Radii are 6px
throughout; the only shadow is on button hover.

`theme.build_css()` returns the whole `<style>` block; `app.py` injects it right
after `st.set_page_config()`:

```python
st.markdown(theme.build_css(), unsafe_allow_html=True)
```

`.streamlit/config.toml` duplicates the colours on purpose — Streamlit paints its
shell from the TOML before Python runs. **Keep the two in sync.**

### Rules carried over (they exist for a reason)

- `.stApp, .stApp *` sets `color`, never `font-family` — a font-family there
  renders Material icons as literal ligature text.
- A primary button's label lives in a nested `<p>`, which `.stApp *` would paint
  dark, so `a[kind="primary"] *` re-asserts white.

### Divergences from the summarizer

- The primary widget is `st.link_button`, which Streamlit renders as an `<a>`;
  `.stButton` rules do not reach it, so the theme styles `.stLinkButton > a`.
- A disabled link button (offline app) is muted to `offline` and gets
  `pointer-events: none`, so it cannot navigate.
- No `sidebar_bg`: this app has no sidebar. `test_theme.py` asserts every palette
  colour is actually applied, which is what caught the dead key.
- The uploader / download / progress / spinner rules are dropped — no such
  widgets here.

## Layout

`layout="wide"`, sidebar collapsed (there is nothing in it). Title, subtitle
caption, divider, then a **two-column grid of cards** (`COLUMNS` in `app.py`),
one per registered app, each an `st.container(border=True)`:

```
### 📚 KI-WissensWiki          <- icon + name
lokales KI-Wissensmanagement-Wiki   <- hint (caption, muted)
🟢 Online                            <- status (caption)
[        Öffnen ↗        ]           <- link_button, primary, full width
```

Below the grid, a divider and a **Status aktualisieren** button that just reruns
the page (status is probed fresh on every load anyway).

**Cards in a row are equal height.** Hints differ in length and wrap to different
line counts, which would otherwise leave the shorter card stunted beside its
neighbour. The theme stretches every card in a row to the tallest
(`align-items: stretch` + `height: 100%`) and pushes the Open button to the
card's foot (`margin-top: auto`) so the buttons line up. Deliberately *not* a
fixed pixel height — the text decides how tall a row is, and a hard-coded height
would clip the next hint someone writes.

All UI strings are German module-level constants at the top of `app.py`. There is
no i18n layer — one language, no need.

## No exit button

Deliberate, and it **overrides the global rule** that every Streamlit app gets a
safe exit button.

The orchestrator is a directory. It starts and stops nothing — not the apps it
lists, and not itself. Two reasons:

1. Killing its own process would trip `tunnel.sh`'s watchdog, which tears the
   tunnel down when port 8550 goes quiet. The public URL would vanish and could
   only be restored from a terminal — a one-way door for a remote user.
2. Because it controls no process, the page is harmless to expose publicly and
   needs no authentication. An exit button would be the one destructive control
   on an unauthenticated page.

Stop it from the terminal: `./tunnel.sh stop`.

`test_app.py::test_there_is_no_exit_button` guards this.
