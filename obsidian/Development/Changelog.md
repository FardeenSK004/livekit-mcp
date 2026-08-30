# Changelog

All notable changes to the `livekit-mcp` project are documented in this file.

## [0.3.1] - 2026-08-30

### Added

- **OAuth 2.1 Server Introspection Client (`AuthClient`)**: Implemented `AuthClient` in `src/livekit_mcp/clients/auth_client.py` executing RFC 7662 token introspection (`POST ${AUTH_SERVER_URL}/api/oauth/introspect`). Integrated seamlessly into `AuthMiddleware` as primary token verification, removing static `JWT_SECRET` requirement from production config (`.env.prod`).

## [0.3.0] - 2026-08-29

### Added

- **Production Multi-Stage Dockerfile**: Implemented a secure, optimized multi-stage build (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`) with unprivileged user `appuser` (UID 10001), layer-cached `uv sync --locked --no-dev`, container healthcheck (`/health`), and entrypoint `livekit-mcp`.

## [0.2.5] - 2026-08-27

### Added

- **Organization Processes & Stages MCP Tool (`fetch_org_processes`)**: Added tool and alias (`receive_org_processes`) to query `MantraAssist-backend` (`GET /api/v1/processes?org_id={org_id}`) with structured process/stage IDs and 10-minute in-memory TTL caching.
- **Provider User ID Injection**: Formatted provider availability strings with `(User ID: <id>)` for automated post-call scheduling resolution.

### Changed

- **Unauthenticated Backend Client**: Removed `x-client-id` and `x-client-secret` headers from `MantraAssistBackendClient`, communicating cleanly with backend services.
- **Root Status API**: Replaced static HTML dashboard with lightweight JSON status response at `/` (`{"status": "working", "service": "livekit-mcp", ...}`).
- **Database Connection Mapping**: Mapped `DATABASE_URL` and `MCP_EVENTS_DB_URL` to local PostgreSQL port 5442 (`mcp_logs_db`).

## [0.2.0] - 2026-08-25

### Added

- **Developer Landing Dashboard & Diagnostics UI**: Designed a clean, dark-themed developer landing page (`src/livekit_mcp/templates/dashboard.html`) showing system diagnostics, uptime, configuration environment, and a dynamically-populated catalog of registered MCP tools and their schemas.
- **Diagnostic Helper API Endpoints**: Created public endpoints `/api/dev/check-db` (checking PostgreSQL availability) and `/api/dev/check-lkt` (verifying LKT voice agent engine status) to support system checks in the landing interface.
- **JWT Development Token Sandbox Endpoint**: Added a POST endpoint `/api/dev/token` (bypassed in production) to sign local JWT testing tokens for developer convenience.
- **Middleware Public Paths Bypass**: Updated `AuthMiddleware` to allow public access to dashboard, dev diagnostics, and token helpers.

### Fixed

- **Doctor Availability Tool kwargs Undefined Bug**: Resolved a linter/runtime issue in `receive_doctor_availability` where `kwargs` was accessed but not defined in the function signature, by adding `**kwargs: Any` to the signature and direct list iteration.
- **Call Tool Output Extraction**: Fixed a compatibility bug in `call_tool_endpoint` handling both FastMCP `CallToolResult` objects and raw `list` content responses.

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
