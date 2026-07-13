# Testing

```bash
uv run pytest        # 46 tests, ~1 s, fully offline
```

The PRD caps the suite at **50 tests**. At 46 there is little headroom: prefer
merging or replacing a test over adding one.

Fully offline in a strong sense — no tunnel, no Cloudflare, and no dependency on
any real app running. Tests that need a live port bind an **ephemeral** one
(`port 0`, the OS picks a free port), so nothing depends on 8520/8530 actually
being up on the developer's machine.

## Map

| File | Tests | Covers |
|---|---|---|
| `test_registry.py` | 15 | `apps.toml` parsing: every field, `url_file` → `Path`, empty registry, and the rejections — missing required field (parametrized ×4), invalid port (parametrized ×3), duplicate ports, unknown field, malformed TOML, missing file. Plus: **the shipped `apps.toml` parses**. |
| `test_status.py` | 10 | URL precedence (`url_file` > `url` > `host:port`), the `APP_HOST` fallback, and the three ways a `url_file` is ignored (missing, empty, garbage). Liveness against a real open/closed port. |
| `test_app.py` | 11 | The page through `streamlit.testing.v1.AppTest`. |
| `test_theme.py` | 7 | `<style>` block shape, every palette colour applied, both fonts imported, the Material-icon ligature guard, white primary label, `pointer-events: none` on a disabled button, custom palette override. |
| `test_config.py` | 3 | Defaults, env overrides, and that the default registry path is absolute (Streamlit's cwd is not guaranteed). |

## Fixtures (`conftest.py`)

- `apps_file` — a valid two-app registry in `tmp_path`.
- `app` — one `App` with no public URL.
- `open_port` — a socket really listening on an ephemeral port, so `is_online()`
  has something true to find.
- `closed_port` — an ephemeral port claimed then released: nothing listens there.

## Testing the page

`AppTest.from_file("src/app.py")` runs the real script. `app.py` reads its config
at import, and `AppTest` re-executes the script on every `.run()`, so pointing
the app at a temporary registry is just `monkeypatch.setenv("APPS_FILE", ...)`.

`st.link_button` has **no `AppTest` accessor**. Reach it through the generic
getter, which exposes the raw proto (`label`, `url`, `disabled`, `type`):

```python
def _links(at):
    return [e.proto for e in at.get("link_button")]
```

The page tests assert the things a user would notice: one card per app, icon and
name and hint rendered, an online app linking to its **public** URL, an offline
app's button **disabled**, an app without a public URL labelled *nur im lokalen
Netzwerk*, `url_file` beating a stale `url`, a broken registry showing an error
and rendering no cards, an empty registry explaining itself, refresh not
exploding — and that **no exit button exists** (see docs/ui.md).
