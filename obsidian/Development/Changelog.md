# Changelog

All notable changes to the `livekit-mcp` project are documented in this file.

## [0.1.0] - 2026-08-22

### Added
- **International Timezone Auto-Detection**: Integrated Google's `phonenumbers` engine in `src/livekit_mcp/utils/timezone.py` to auto-detect caller country/timezone from phone number (`+1` US -> EDT, `+44` UK -> GMT/BST, `+91` India -> IST, `+971` UAE -> GST, `+61` Australia -> AEST) and convert raw UTC slots dynamically into localized 12-hour format.
- **Multi-Provider Array Support**: Updated `receive_doctor_availability` in `src/livekit_mcp/tools/doctor_availability.py` to support arrays of multiple doctors and their respective UTC schedules.
- **Direct Tool Call Route (`/api/tools/call`)**: Added HTTP POST endpoint to `src/livekit_mcp/server.py` allowing internal microservices like `lkt` to invoke MCP tools synchronously with JWT Bearer authentication.
- **Token Generator CLI**: Created `scripts/generate_token.py` utility for generating HS256 JWT access tokens.
- **Doctor Availability Receiver Tool**: Implemented `receive_doctor_availability` in `src/livekit_mcp/tools/doctor_availability.py` to accept pre-computed doctor schedules and slots from `MantraAssist-backend`.
- **Integration Specs (`structure.json` & `format.json`)**: Created minimal 1:1 schema specification files for backend developer reference.
- **Provider Availability Search Tool**: Implemented `search_provider_availability` in `src/livekit_mcp/tools/providers.py` to query `assist_db` (`provider_availability` + `providers` + `provider_to_organization`).
- **Database Client**: Added `DatabaseClient` in `src/livekit_mcp/clients/db_client.py` using `asyncpg` with connection pooling.
- **Test Suite**: 27 automated unit & integration tests passing 100% across all tools, timezones, and auth layers.
- Scaffolding with `uv`, `pyproject.toml`, Starlette ASGI MCP 2.0 SSE transport, and HS256 shared JWT authentication.
- Agentic memory in `obsidian/` and `AGENTS.md`.
