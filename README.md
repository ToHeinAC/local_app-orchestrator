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
- Public-URL aware: links work from outside when an app has its own tunnel
  (see [Remote access](#remote-access)).

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
url      = "https://example.trycloudflare.com/"   # optional
url_file = "/tmp/neue-app-url.txt"                # optional
```

Only `name`, `hint`, `icon` and `port` are required. See [docs/registry.md](docs/registry.md).

## Remote access

A link is resolved by the browser that clicks it, so `http://localhost:8530` only
works from this machine or the LAN. To reach an app from outside, that app needs
its **own** public URL — the orchestrator's tunnel carries port 8550 and nothing
else.

The orchestrator picks an app's URL in this order:

1. `url_file` — the file the app's `tunnel.sh` writes its current public URL to.
   Quick-tunnel URLs rotate on restart, so reading the file keeps links fresh.
2. `url` — a static public URL.
3. `http://<APP_HOST>:<port>` — the fallback. The card says "nur im lokalen
   Netzwerk erreichbar", because it is.

Expose the orchestrator itself with:

```bash
./tunnel.sh          # start app + Cloudflare quick tunnel, print the public URL
./tunnel.sh stop
```

## Tests

```bash
uv run pytest        # 40 tests, fully offline
```

## Documentation

- [IMPLEMENTATION.md](IMPLEMENTATION.md) — current state and module map
- [docs/](docs/) — architecture, registry, UI, testing
- [PRD.md](PRD.md) — original goals and acceptance criteria
- [AGENTS.md](AGENTS.md) — collaboration rules for AI coding tools

## License

Apache-2.0 — see [LICENSE](LICENSE).
