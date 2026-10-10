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
| `url` | no | Public URL. For an app behind the nginx proxy: `https://ai.brenk.com/<path>/`, trailing slash included. |
| `url_file` | no | File holding the app's *current* public URL. Wins over `url`. For an app on a rotating quick tunnel instead of the proxy. |
| `section` | no | Panel heading. Apps with the same section share one bordered panel with a two-column grid; panels appear in the order their section is first used, apps in registry order within a panel. Default `""` = a panel without heading. |

Unknown fields are rejected, so a typo like `urlfile =` fails loudly instead of
being silently ignored.

## Adding an app

```toml
[[apps]]
name     = "Neue App"
hint     = "kurze Beschreibung"
icon     = "🚀"
port     = 8540
url      = "https://ai.brenk.com/neu/"
```

That is all *here*. Restart is not needed — the registry is read on every page
load; the Refresh button re-reads it. The app's public URL itself has two more
sides to it (an nginx path, a matching `baseUrlPath`) — see
[reverse-proxy.md](reverse-proxy.md#adding-an-app).

## URL resolution

Resolution order: **`url_file` → `url` → `http://<APP_HOST>:<port>`**.

A link is resolved by the browser that clicks it. `http://localhost:8530` works
only from this server or its LAN. To reach an app from outside, that app needs
its own public URL.

Every registered app now has a **permanent** one, served by the nginx reverse
proxy at one path per app:

| App | Public URL |
|---|---|
| BrAIn (8511) | `https://ai.brenk.com/brain/` |
| KI-WissensWiki (8520) | `https://ai.brenk.com/wiwi/` |
| KI-Zusammenfassung (8530) | `https://ai.brenk.com/smrz/` |
| KI-Übersetzer (8560) | `https://ai.brenk.com/trns/` |

The **trailing slash is required**, not cosmetic: Streamlit's asset links are
relative, and without the slash they resolve at the site root and the app renders
blank. [reverse-proxy.md](reverse-proxy.md) explains the mechanics.

### `url_file`, and when you still want it

Cloudflare **quick-tunnel URLs rotate on every tunnel restart**, so a URL pasted
into `url` goes stale and becomes a dead link. An app on a quick tunnel therefore
names the *file* its `tunnel.sh` writes the current URL to, and the orchestrator
reads it at page load: restart the tunnel, refresh the page, the link is fresh.

No app uses this today — they are all behind the proxy. The mechanism stays for
an app that is not (yet) in the nginx config. Keep `url` as well if you like — it
is the fallback when the tunnel, and its file, is down.

A `url_file` that is missing, empty, or does not start with `http://`/`https://`
is ignored rather than treated as an error: a down tunnel is normal, and linking
the browser at a log line would be worse than falling back.

### The fallback URL

The last resort, `http://<APP_HOST>:<port>`, is **wrong for an app that has a
`baseUrlPath`** — that app answers 404 at its port's root and lives at
`http://<host>:<port>/<path>/` instead. The orchestrator does not know about
`baseUrlPath`, and deliberately so: every registered app has a permanent `url`,
so the fallback never fires for one. It only appears for an app registered
without any public URL, which by definition has no proxy path either. If that
changes, the honest fix is a `base_path` field in the registry — not guessing in
`status.resolve()`.

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
