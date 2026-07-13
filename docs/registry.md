# Registry (`apps.toml`)

The list of apps the orchestrator routes to. Adding an app is a config change,
never a code change.

## Schema

One `[[apps]]` block per app.

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Display name on the card. |
| `hint` | yes | One-line description under the name. |
| `icon` | yes | Emoji left of the name. |
| `port` | yes | Port the app listens on, on this server. 1–65535, unique across the registry. |
| `url` | no | Static public URL (e.g. a tunnel). |
| `url_file` | no | File holding the app's *current* public URL. Wins over `url`. |
| `featured` | no | `true` → a full-width card above the divider, ahead of the grid. Default `false`. For the entry point people should land on. |

Unknown fields are rejected, so a typo like `urlfile =` fails loudly instead of
being silently ignored.

## Adding an app

```toml
[[apps]]
name     = "Neue App"
hint     = "kurze Beschreibung"
icon     = "🚀"
port     = 8540
url_file = "/tmp/neue-app-url.txt"
```

That is all. Restart is not needed — the registry is read on every page load; the
Refresh button re-reads it.

## URL resolution, and why `url_file` exists

Resolution order: **`url_file` → `url` → `http://<APP_HOST>:<port>`**.

A link is resolved by the browser that clicks it. `http://localhost:8530` works
only from this server or its LAN. To reach an app from outside, that app needs
its own public URL — the orchestrator's own tunnel carries port 8550 and nothing
else.

Cloudflare **quick-tunnel URLs rotate on every tunnel restart**, so a URL pasted
into `url` goes stale and becomes a dead link. Each app's `tunnel.sh` already
writes its current URL to a file:

| App | URL file |
|---|---|
| KI-WissensWiki (8520) | `/tmp/wiki-app-url.txt` |
| KI-Zusammenfassung (8530) | `/tmp/summarizer-app-url.txt` |

BrAIn (8511) is the exception: it has a **permanent** URL on a real domain
(`https://ai.brenk.com/`), so it needs no `url_file` and cannot go stale.

Naming the *file* in the registry means the orchestrator reads whatever is
current at page load. Restart an app's tunnel, refresh the page, the link is
fresh. Keep `url` as well if you like — it is the fallback when the tunnel (and
its file) is down.

A `url_file` that is missing, empty, or does not start with `http://`/`https://`
is ignored rather than treated as an error: a down tunnel is normal, and linking
the browser at a log line would be worse than falling back.

## Status

`port` drives the liveness probe (TCP connect to `localhost:<port>`), and the
resolved URL drives the button:

| Port listening | Public URL known | Card |
|---|---|---|
| yes | yes | 🟢 Online — Open → public URL |
| yes | no | 🟢 Online, *nur im lokalen Netzwerk erreichbar* — Open → `http://host:port` |
| no | — | ⚪ Offline — button disabled |

The middle row is labelled rather than hidden: the link genuinely works for you
at the machine, and genuinely will not work for a remote visitor.

## Errors

`RegistryError` names the culprit and the page stops rather than rendering a
partial directory. Rejected: missing required field, port out of range or not an
integer, duplicate port, unknown field, malformed TOML, missing file. An **empty**
registry is valid — the page says nothing is registered yet.
