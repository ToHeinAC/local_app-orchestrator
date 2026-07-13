# User Stories

## User
- As a user, I want to see a single page application with a clean and modern UI (same theme as https://github.com/ToHeinAC/local_summarizer) that routes to available apps running as a service on different ports of the server, so that I can easily chose and use all available apps.

## Development
- As a developer, I want to implement every feature using claude code (steps: catch feature (from developer and/or from an implementation plan), implement feature, test feature, document feature), so that I can deliver high-quality features quickly and efficiently.
- As a developer, I want to have implemented: App name, app icon, app port (where the service actually runs on the server and where to route to) such that I can easily add new apps to the orchestrator.
- As a developer, I want the implementations to pass a test suite that covers the main functionality as well as edge cases (but in total not more than 50 tests; remove those already working consistently or merge tests that are testing similar things), so that I can ensure the quality of the code.
- As a developer, I want to document every feature I implement in a way that is easy to understand and maintain, so that I can ensure the code is maintainable and understandable.
- As a developer, I want to use a consistent coding style and follow best practices, so that I can ensure the code is maintainable.
- As a developer, I want to use a consistent project structure and organization, so that I can ensure the code is easy to navigate and understand.
- As a developer, I want to use a consistent naming convention for variables, functions, and files, so that I can ensure the code is easy to read and understand.
- As a developer, I want to use a consistent error handling strategy, so that I can ensure the code is robust and reliable.
- As a developer, I want to see the KISS (Keep It Simple, Stupid) principle applied to every feature I implement, so that I can ensure the code is simple and easy to understand.

## Acceptance Criteria
- All implementation must be under the Apache Licence 2.0 or more permissive (e.g. MIT).
- All implementation must be in python and the pythonic way of implementation.
- `uv` is used for the virtual python environment setup and the running. Dependencies shall be defined in `pyproject.toml` and installed via `uv`.
- Use python-dotenv for the environmental variable handling.
- All domain Python modules live in `src/`. Run with `uv run streamlit run src/app.py --server.port 8550`.
  - Port **8550** is the project's chosen Streamlit port (avoids the default 8501 and a collision with another local app on 8520). Configurable via `APP_PORT` in `.env`.
- Use https://github.com/ToHeinAC/local_app-orchestrator as git remote repo
- The orchestrator **routes only**: it links to apps on their own ports and never proxies, embeds, starts or stops them. It therefore needs no authentication.
- **No exit button.** This overrides the global Streamlit rule that every app gets one: the orchestrator kills no process, its own included. Stop it from the terminal (`./tunnel.sh stop`), which also tears down its tunnel cleanly.