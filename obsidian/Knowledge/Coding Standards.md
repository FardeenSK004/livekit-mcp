# Coding Standards

## 1. Code Style & Formatting
- **Linter & Formatter:** Use `ruff` configured in `pyproject.toml`.
- **Target Version:** Python 3.11+.
- **Line Length:** 100 characters maximum.
- **Type Annotations:** All functions and methods must have complete type hints (`from typing import ...`).
- **Docstrings:** Use Google-style or standard Sphinx docstrings for all modules, classes, and tools.

## 2. Asynchronous I/O
- All network requests (HTTP, SSE, WebSockets) must use `async`/`await`.
- Use `httpx.AsyncClient` for external HTTP communication.
- Never use blocking calls (`time.sleep`, synchronous `requests`) inside async paths.

## 3. Error Handling
- Never silence errors silently.
- Return descriptive error messages adhering to MCP error formats.
- Log exceptions with appropriate context and levels (`logger.error(...)`).

## 4. Configuration
- Never hardcode URLs, ports, or credentials.
- All configuration must go through `src/livekit_mcp/config.py` using `pydantic-settings`.
