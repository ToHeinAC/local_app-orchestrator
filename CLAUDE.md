# CLAUDE.md

The shared, vendor-neutral collaboration rules for AI coding tools live in [AGENTS.md](AGENTS.md) (also read by Codex, Cursor, etc.). Claude Code reads *this* file, so the import below pulls in the shared rules — one source of truth for every tool.

@AGENTS.md

## Project at a glance
A single-page directory of the local AI apps on this server. One card per app (icon, name, hint, live status) with an Open button that routes straight to the app on its own port. Streamlit only — no LLM, no LangChain, no vector DB.

```bash
uv sync
uv run streamlit run src/app.py --server.port 8550   # port per PRD.md
uv run pytest                                        # 46 tests, fully offline
```

**Hard boundaries** (see AGENTS.md §5.4): the orchestrator **routes but never proxies**, **never starts or stops** the apps it lists, and has **no exit button**. It controls nothing, so it needs no auth.

## Documentation map
Start with [IMPLEMENTATION.md](IMPLEMENTATION.md) @IMPLEMENTATION.md — current state, module map, key decisions. Deep detail per component:

- [docs/architecture.md](docs/architecture.md) @docs/architecture.md — layers, data flow, why routing works the way it does
- [docs/registry.md](docs/registry.md) @docs/registry.md — `apps.toml` schema, adding an app, URL resolution and the tunnel problem
- [docs/ui.md](docs/ui.md) @docs/ui.md — Forest palette, CSS injection, card layout, the no-exit-button decision
- [docs/testing.md](docs/testing.md) @docs/testing.md — test map and fixtures

[PRD.md](PRD.md) holds the original goals and acceptance criteria.

## Claude Code specifics
- Slash commands: `.claude/commands/` (`commit-git`, `create-prd`, `documentation-update`). Skills: `.claude/skills/` (`code_review`, `restart-app`).
- Permissions/config: shared safe allows are committed in `.claude/settings.json`; machine-personal ones stay in `.claude/settings.local.json` (gitignored).
