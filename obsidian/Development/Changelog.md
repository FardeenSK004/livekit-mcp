# Changelog

All notable changes to the `livekit-mcp` project are documented in this file.

## [0.1.0] - 2026-08-20

### Added
- Initial project scaffolding using Python 3.11+ and `uv`.
- Configured `pyproject.toml` with `mcp`, `starlette`, `uvicorn`, `pydantic-settings`, `pyjwt[crypto]`, `httpx`, `pytest`, `ruff`.
- `AGENTS.md` and Obsidian knowledge base (`obsidian/`) for permanent agentic memory.
- `src/livekit_mcp/config.py` Pydantic Settings with full environment validation.
- `src/livekit_mcp/auth/jwt.py` for HS256 JWT decoding and validation matching `mantra-auth`.
- `src/livekit_mcp/auth/middleware.py` Starlette authentication middleware supporting headers and query tokens.
- `src/livekit_mcp/clients/lkt_client.py` and `auth_client.py` async HTTP client stubs.
- `src/livekit_mcp/tools/greeting.py` sample greeting tool.
- `src/livekit_mcp/server.py` Starlette app and MCP server factory.
- Comprehensive unit and integration test suite in `tests/`.
