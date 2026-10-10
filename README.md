# Local App Orchestrator

A single-page directory of the local AI apps running on this server. Each app has
a card — icon, name, hint, live status — and an Open button that routes straight
to the app on its own port. Same Forest look as
[local_summarizer](https://github.com/ToHeinAC/local_summarizer).

The orchestrator **routes but never proxies**. It starts and stops nothing, so it
is safe to expose publicly.

## Features

- One card per app: icon, display name, hint, status, Open button.
- Live status: a TCP probe per port on each page load — online apps are linkable,
  offline ones are greyed out.
- Add an app by appending five lines to `apps.toml`. No code change.
- Public-URL aware: links work from outside when an app has a public URL of its
  own (see [Remote access](#remote-access)).

## Requirements

Python ≥ 3.12 and [uv](https://docs.astral.sh/uv/).

## Setup & run

```bash
uv sync
cp .env.example .env          # optional — the defaults work as-is
uv run streamlit run src/app.py --server.port 8550
```

Port **8550** avoids Streamlit's default 8501 and the ports of the apps it routes
to. Override with `APP_PORT` in `.env`.

## Adding an app

Append to `apps.toml`:

```toml
[[apps]]
name     = "Neue App"
hint     = "kurze Beschreibung"
icon     = "🚀"
port     = 8540
url      = "https://ai.brenk.com/neu/"   # optional
```

Only `name`, `hint`, `icon` and `port` are required. See [docs/registry.md](docs/registry.md).
Giving the app a public URL also means giving it a path in the reverse proxy —
[docs/reverse-proxy.md](docs/reverse-proxy.md#adding-an-app).

## Remote access

A link is resolved by the browser that clicks it, so `http://localhost:8530` only
works from this machine or the LAN. To reach an app from outside, that app needs
a public URL of its own.

An nginx reverse proxy on **`ai.brenk.com`** provides them — the orchestrator at
`/`, one path per app:

| URL | App |
|---|---|
| `https://ai.brenk.com/` | the orchestrator itself |
| `https://ai.brenk.com/brain/` | BrAIn (8511) |
| `https://ai.brenk.com/wiwi/` | KI-WissensWiki (8520) |
| `https://ai.brenk.com/smrz/` | KI-Zusammenfassung (8530) |
| `https://ai.brenk.com/trns/` | KI-Übersetzer (8560) |

Each app carries a `baseUrlPath` matching its path, and nginx and the app must
agree or the app renders blank. The config to install and the reasoning behind it
are in [docs/reverse-proxy.md](docs/reverse-proxy.md); the orchestrator itself
proxies nothing either way.

The orchestrator picks an app's URL in this order:

1. `url_file` — a file holding the app's current public URL, re-read on every
   page load. For an app on a Cloudflare quick tunnel, whose URL rotates on
   restart. Unused now that the apps are behind the proxy.
2. `url` — a static public URL. What all four apps use.
3. `http://<APP_HOST>:<port>` — the fallback. The card says "nur im lokalen
   Netzwerk erreichbar", because it is.

## Tests

```bash
uv run pytest        # 50 tests, fully offline
```

## Documentation

- [IMPLEMENTATION.md](IMPLEMENTATION.md) — current state and module map
- [docs/](docs/) — architecture, registry, UI, testing
- [PRD.md](PRD.md) — original goals and acceptance criteria
- [AGENTS.md](AGENTS.md) — collaboration rules for AI coding tools

## License

Apache-2.0 — see [LICENSE](LICENSE).
