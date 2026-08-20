# Conventions

## Module Organization
- `src/livekit_mcp/config.py`: Single source of truth for runtime configuration.
- `src/livekit_mcp/auth/`: All security, token decoding, and middleware logic.
- `src/livekit_mcp/clients/`: Outbound HTTP clients to other services (`lkt`, `mantra-auth`).
- `src/livekit_mcp/tools/`: Domain-isolated tool definitions.
- `src/livekit_mcp/server.py`: Server assembly and lifecycle management.

## Logging
- Each module initializes its own logger: `logger = logging.getLogger(__name__)`.
- Structured log format with timestamp, level, module, and message.

## Testing
- Tests live in `tests/`.
- Test files named `test_*.py`.
- Run tests via `uv run pytest`.
