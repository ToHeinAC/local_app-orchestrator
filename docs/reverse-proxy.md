# Reverse proxy (`ai.brenk.com`)

How the apps get permanent public URLs. The config to install lives in
[deploy/ai.brenk.com.conf](../deploy/ai.brenk.com.conf).

This does **not** cross the "route, never proxy" boundary in
[AGENTS.md](../AGENTS.md) §5.4. The orchestrator still only links. The proxying
happens outside it, on a separate machine, and the orchestrator neither knows nor
cares — it just has a `url` per app in `apps.toml`.

## The setup

```
browser --https--> ai.brenk.com (37.24.163.90)
                        |
                   nginx 172.16.4.11:444   <- SSL termination, path routing
                        |
        +---------------+---------------+---------------+---------------+
        |               |               |               |               |
   /  -> :8550     /brain/ -> :8511  /wiwi/ -> :8520  /smrz/ -> :8530  /trns/ -> :8560
   orchestrator    BrAIn             WissensWiki      Zusammenfassung  Übersetzer
```

nginx is reachable at `172.16.4.11` port **222** (SSH); the login is Horst's. The
config is `/etc/nginx/sites-enabled/ai.brenk.com.conf`, activated with
`systemctl reload nginx.service` — **reload, never restart**: a restart drops
every connection, other domains included.

## The rule: two sides must agree

An app served under a subpath needs **both**, and they must match:

| Side | Setting |
|---|---|
| nginx | `location /wiwi/` → `proxy_pass http://172.16.4.112:8520;` (**no** trailing slash on `proxy_pass`) |
| the app | `.streamlit/config.toml` → `[server] baseUrlPath = "wiwi"` |

The orchestrator itself is the exception: it lives at `/` and must have **no**
`baseUrlPath`.

## Why, exactly

Streamlit emits **relative** asset links — `./static/js/index.<hash>.js` — and it
does so *regardless* of `baseUrlPath`. There is no absolute `/wiwi/static/...` in
the HTML, ever. What decides where those links land is the **trailing slash** of
the page they sit on:

| Page in the browser | `./static/x.js` resolves to |
|---|---|
| `/wiwi` | `/wiwi` is not a directory → `/static/x.js` → hits `location /` → the orchestrator's bundle → blank page |
| `/wiwi/` | `/wiwi/static/x.js` → correct |

So `baseUrlPath` does not rewrite links. It moves the whole app under a path, and
relative links then resolve inside it.

Measured against Streamlit 1.59.2 with `baseUrlPath=wiwi`:

| Request | Response |
|---|---|
| `/` | 404 |
| `/wiwi` | 307 → `/wiwi/` |
| `/wiwi/` | 200 |
| `/wiwi/_stcore/health` | 200 |

Two consequences worth knowing:

**Without `baseUrlPath`, the failure is silent.** A request for `/wiwi` returns
**200**, not 404 — Streamlit reads `wiwi` as a multipage page name and serves the
app's index. The HTML arrives, the assets do not. That is why the symptom is a
blank page whose source looks perfectly fine.

**The app can only be reached under its path now.** `http://172.16.4.112:8520/`
answers 404; the app is at `http://172.16.4.112:8520/wiwi/`. This is the price of
`baseUrlPath` and it is unavoidable — see [registry.md](registry.md#the-fallback-url)
for what it means for the orchestrator's fallback URL.

## Two gotchas the config handles

**The redirect must happen in nginx.** Streamlit redirects `/wiwi` → `/wiwi/`
itself, so in principle the slash is optional. But it builds that redirect as an
*absolute* URL from the `Host` header and **ignores `X-Forwarded-Proto`**, so
behind SSL termination it emits `http://ai.brenk.com/wiwi/` — an HTTPS→HTTP
downgrade. `location = /wiwi { return 308 /wiwi/; }` answers in nginx, and the
request never reaches Streamlit without its slash.

**`Connection` must be conditional.** Streamlit needs a WebSocket
(`/_stcore/stream`). Setting `proxy_set_header Connection` to a fixed value
breaks either the WebSocket or plain HTTP. The `map $http_upgrade
$connection_upgrade` block picks per request. (The previous config set
`Connection` twice — `"upgrade"`, then `keep-alive` — which is contradictory; the
map replaces both.)

**`location /wiwi/` with the slash, not `location /wiwi`.** Prefix matching would
otherwise also catch `/wiwitest`. The `location = /wiwi` next to it handles the
slashless case exactly.

## Adding an app

1. Pick a short path (`/neu`) and give the app its port.
2. In the app's `.streamlit/config.toml`: `[server] baseUrlPath = "neu"`.
   Put it in the config file, not on the command line — then nobody can forget it
   at startup.
3. In `deploy/ai.brenk.com.conf`: copy a redirect + proxy block pair, set path
   and port.
4. Install and `nginx -t && systemctl reload nginx.service`.
5. In `apps.toml`: `url = "https://ai.brenk.com/neu/"` (with trailing slash).

## Why not subdomains

`wiwi.brenk.com` per app would need no `baseUrlPath`, no slash handling and no
redirect — `proxy_pass` to `/` and done. It needs a DNS record per app and a
certificate that covers the names. Worth revisiting if `brenk.com`'s certificate
turns out to be a wildcard; the subpath setup was chosen deliberately over it.

## What this replaced

Cloudflare quick tunnels, one per app, whose URLs rotate on every restart — the
reason `url_file` exists in the registry. The apps behind nginx now have
permanent URLs and need neither. See [registry.md](registry.md).
