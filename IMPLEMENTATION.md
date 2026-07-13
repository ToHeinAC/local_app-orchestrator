# IMPLEMENTATION.md

Current state of the Local App Orchestrator. Original goals: [PRD.md](PRD.md).
Deep detail per component: [docs/](docs/).

## What it is

A Streamlit single-page app on port **8550**. It reads a registry of local apps
from `apps.toml`, probes each app's port, and renders one card per app with an
Open button pointing at that app's own service.

It **routes only** — no proxy, no iframe, no process control, no auth, no exit
button. See [AGENTS.md](AGENTS.md) §5.4 for why each of those is a boundary
rather than a missing feature.

## Module map

| Module | Responsibility |
|---|---|
| `src/app.py` | The page: page config, CSS, title, card grid, refresh button. |
| `src/registry.py` | Parses `apps.toml` into validated frozen `App` records. Raises `RegistryError` naming the bad entry. |
| `src/status.py` | `resolve()` picks an app's URL; `is_online()` TCP-probes its port; `check()` returns both as a `Status`. |
| `src/config.py` | Scalars from the environment (python-dotenv) into a frozen `Config`. |
| `src/theme.py` | Forest palette + `build_css()`, ported from `local_summarizer`. |
| `apps.toml` | The app registry. Adding an app = five lines here, no code change. |

Data flow, once per page load:

```
apps.toml --registry.load_apps--> [App]
                                    |
                     status.check(app, host, timeout)
                          |                    |
                  resolve(url)          is_online(port)
                  url_file -> url       TCP connect
                  -> http://host:port
                                    |
                                 app.py card
```

## Key decisions

**Registry in TOML, not `.env`.** python-dotenv handles the scalars (`APP_PORT`,
`APP_HOST`, `PROBE_TIMEOUT`), but a *list of records* is miserable to encode in
environment variables. `apps.toml` gives comments, a copy-paste template, and
validation. See [docs/registry.md](docs/registry.md).

**URL files beat static URLs.** Cloudflare quick-tunnel URLs rotate on every
restart. Each app's `tunnel.sh` writes its current URL to a file, so the registry
names the *file*; the orchestrator reads it at page load and the link is never
stale. Resolution order: `url_file` → `url` → `http://<host>:<port>`.

**Local-only links are labelled as such.** An app with no public URL falls back
to `http://<host>:<port>`, which only works from this server or its LAN — a link
resolved by a remote visitor's browser would hit *their* machine. The card says
so rather than handing over a link that silently hangs.

**No exit button**, overriding the global Streamlit rule. The orchestrator kills
no process, its own included; stopping it would also drop its tunnel via
`tunnel.sh`'s watchdog. Stop it from the terminal.

**No `sidebar_bg` in the palette.** The app has no sidebar; a test asserts every
palette colour is actually applied, which caught the dead key.

## Status semantics

| Port listening | Public URL known | Card |
|---|---|---|
| yes | yes | 🟢 Online — Open → public URL (works anywhere) |
| yes | no | 🟢 Online, *nur im lokalen Netzwerk* — Open → `http://host:port` |
| no | — | ⚪ Offline — button disabled |

## Registered apps

| App | Port | Public URL | Layout |
|---|---|---|---|
| 🧠 BrAIn | 8511 | `https://ai.brenk.com/` (permanent) | featured, full width |
| 📚 KI-WissensWiki | 8520 | `/tmp/wiki-app-url.txt` (rotates) | grid |
| 🔎 KI-Zusammenfassung | 8530 | `/tmp/summarizer-app-url.txt` (rotates) | grid |

`featured = true` lifts an app out of the grid into a full-width card above the
divider. The split is data-driven; `app.py` names no app.

## Tests

50 tests, fully offline — **at** the PRD's 50 cap. Adding a test now means
merging or dropping one. `uv run pytest`. Map: [docs/testing.md](docs/testing.md).

## Run

```bash
uv sync
uv run streamlit run src/app.py --server.port 8550
./tunnel.sh          # + Cloudflare quick tunnel, prints the public URL
./tunnel.sh stop
```
