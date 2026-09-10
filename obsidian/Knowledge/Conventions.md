# Conventions

## Module Organization
- `src/livekit_mcp/config.py`: Single source of truth for runtime configuration.
- `src/livekit_mcp/auth/`: All security, token decoding, and middleware logic.
- `src/livekit_mcp/clients/`: Outbound HTTP/DB clients — `lkt`, `mantra-auth` (`auth_client`), `MantraAssist-backend` (`backend_client`), Postgres (`db_client`).
- `src/livekit_mcp/routes/`: HTTP surface (`api.py` — health, root JSON, `/tools/call`, `/dev/*`).
- `src/livekit_mcp/utils/`: Cross-cutting helpers — telemetry (`db_logger.py`), timezone/phone (`timezone.py`).
- `src/livekit_mcp/tools/`: Domain-isolated tool definitions (one module per tool family + `register_*` entrypoint).
- `src/livekit_mcp/server.py`: Server assembly and lifecycle management (registers 5 tool modules → 6 tool names with the processes alias).

## Tool Registration
- Each tool module exposes `register_*_tool(server, settings, backend_client)` and is wired in `create_mcp_server()`.
- Keep `tools/__init__.py` re-exports in sync when adding modules (currently `client_recognition` + `department_list` are registered in `server.py` but missing from `__init__` exports — fix pending).

## Backend Client
- `MantraAssistBackendClient` is unauthenticated; always send `ngrok-skip-browser-warning: 69420`.
- Availability contract is a fixed UTC schema (`org_id`, `date`, `datetime`, `doc_name`, `department`, `caller_phone`) over `GET /v1/webhooks/mcp` with `POST` fallback; default caller tz `Asia/Kolkata`.
- New webhook lookups fail open (return `None`/`[]`/`{"org_id","departments": []}`) so live calls are never blocked; log with `[MA-BACKEND]` / `[MCP-TOOL]` prefixes.
- TTL caches: `_processes_cache` and `_departments_cache` (10 min per `org_id`); only non-empty payloads are cached.

## Logging
- Each module initializes its own logger: `logger = logging.getLogger(__name__)`.
- Structured log format with timestamp, level, module, and message.

## Testing
- Tests live in `tests/` (currently missing as of 2026-09-08 — re-scaffold before claiming coverage).
- Test files named `test_*.py`.
- Run tests via `uv run pytest`.
