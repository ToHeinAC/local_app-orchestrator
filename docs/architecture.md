# Architecture

## Layers

```
src/app.py        Streamlit page — the only module that renders anything
  |
  +-- src/theme.py      CSS (pure string building, no state)
  +-- src/config.py     scalars from .env  -> Config (frozen)
  +-- src/registry.py   apps.toml          -> [App] (frozen)
  +-- src/status.py     App + host/timeout -> Status (frozen)
```

Nothing below `app.py` imports Streamlit, and nothing imports anything else in
`src/` except `status.py`, which needs the `App` type. Every module is plain
Python, side-effect free apart from `config.load_dotenv()` and the socket probe.

## Data flow (once per page load)

1. `config.load_config()` — `APP_HOST`, `APPS_FILE`, `PROBE_TIMEOUT`.
2. `registry.load_apps(path)` — parse and validate `apps.toml`. A malformed
   registry raises `RegistryError`; `app.py` shows the message and `st.stop()`s,
   because half a directory is worse than an honest error.
3. Per app, `status.check(app, host, timeout)`:
   - `resolve()` — `url_file` → `url` → `http://<host>:<port>`, plus a `public`
     flag saying whether that URL works from outside this machine.
   - `is_online()` — TCP connect to `localhost:<port>`, `PROBE_TIMEOUT` seconds.
4. `app.py` renders a card per app in a two-column grid.

No caching. Two apps × a 0.3 s worst-case probe against localhost is cheap, and a
cache would show stale status right after starting an app — the opposite of what
this page is for.

## Why routing works this way

The orchestrator **links**; it does not proxy. Each app is an independent
Streamlit server on its own port, and the Open button simply navigates the
browser there.

The consequence to understand: **a link is resolved by the browser that clicks
it.** `http://localhost:8530` reaches the summarizer only if the browser runs on
this server (or on the LAN, via `APP_HOST`). A visitor coming through the
orchestrator's Cloudflare tunnel who clicks a localhost link hits *their own*
port 8530.

A Cloudflare quick tunnel maps **one public URL to one local port**. The
orchestrator's tunnel carries 8550 and nothing else. So for an app to be
reachable from outside, that app needs its **own** tunnel, and the orchestrator
needs to know its URL — hence `url` / `url_file` in the registry.

Alternatives considered and rejected:

- **Reverse proxy** (`/app/wiki` → `:8520`, one tunnel for everything). Correct
  in principle, but Streamlit is a WebSocket app: it needs an HTTP+WS relay in
  front, every app relaunched with a matching `--server.baseUrlPath`, and it
  brings XSRF/static-asset breakage. Too much machinery for a directory page.
- **iframe embedding.** Same localhost problem, unfixable — the iframe URL is
  resolved by the visitor's browser too — plus it needs CORS/XSRF disabled on
  every embedded app.
- **A named Cloudflare tunnel** with hostname→port ingress rules. This is the
  *right* long-term answer: one tunnel, permanent URLs, no `/tmp` files. It needs
  a domain in Cloudflare DNS, which this setup does not have. (`~/.cloudflared/config.yml`
  currently lists `*.trycloudflare.com` hostnames, which cannot work for a named
  tunnel.) If a domain appears, drop `url_file` and hard-code the hostnames.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `APP_PORT` | `8550` | Port the orchestrator serves on. |
| `APP_HOST` | `localhost` | Host for the fallback URL of apps with no public URL. Set to the LAN IP to make fallback links work from other machines on the network. |
| `APPS_FILE` | `<repo>/apps.toml` | The registry. Absolute by default — Streamlit's cwd is not guaranteed. |
| `PROBE_TIMEOUT` | `0.3` | Seconds before a port counts as offline. Every app is probed on every page load, so keep it small. |

`.streamlit/config.toml` carries the same palette as `theme.py` and pins the port
to 8550; Streamlit paints its shell from that file before Python runs, so the two
must stay in sync.
