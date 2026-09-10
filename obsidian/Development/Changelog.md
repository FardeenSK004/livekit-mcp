# Changelog

All notable changes to the `livekit-mcp` project are documented in this file.

## [Unreleased] — vault sync 2026-09-10

### Added

- **Department Discovery docs:** New `Features/Department Discovery Tool.md` for `get_org_departments` (`GET /v1/webhooks/mcp/departments`, TTL cache, tolerant normalization).

### Fixed (docs only, no code changes)

- Rewrote `Features/Doctor Availability Receiver Tool.md` to the live signature (pre-supplied slots OR `GET+POST /v1/webhooks/mcp` query + `assist_db` fallback, UTC-slot localization).
- Corrected `Features/Client Recognition Tool.md` (metadata `ai_summaries`/`custom_fields`, `phone_number` param, `/v1/webhooks/mcp/lead` contract).
- Fixed `Features/Org Processes Tool.md` fallback chain to `/v1/...` paths.
- Fixed `Architecture/APIs.md` + `Architecture/Security & Auth.md` route prefixes (`/tools/call`, `/dev/*`).
- Refreshed `Home.md` (6 tool names), `Architecture/Overview.md` (topology + backend endpoints), `Context/Repository Map.md` (HEAD `0de282c`), `Knowledge/Conventions.md` (contracts, caches, exports).
- Recorded remaining drift: missing `docker-compose.yml`, missing `tests/` suite, `tools/__init__.py` export gap (`client_recognition` + `department_list`), `pyproject.toml` version drift (`0.1.0` vs `0.3.3`), stale `Greeting Tool.md`, stale `README.md` route/tool docs.

## [Unreleased] — department branch 2026-09-09 (`a11f3f4` → `7d88c33` → merge `0de282c`)

### Added

- **Organization Department Discovery (`get_org_departments`)**: Cached MCP tool fetching departments/specialties from `GET /v1/webhooks/mcp/departments?org_id={org_id}` for broad-symptom clarification; normalizes `departments`/`specializations`/`data`/`results` shapes into sorted `{"org_id", "departments"}`.
- **Client Recognition Metadata**: `recognize_client` now returns `client_metadata` with `ai_summaries` and `custom_fields`, unwrapping `data`/`result` envelopes with `name`/`full_name` fallbacks.

### Changed

- **Route Prefix Simplification**: `routes/api.py` now mounts `/tools/call` and `/dev/*` (previously `/api/tools/call`, `/api/dev/*`).
- **LKT Active-Calls Path**: `get_active_calls()` now uses `/v1/dashboard/active-calls` (previously `/api/v1/...`).
- **Doctor Availability Endpoint Reference**: Tool description now references `/v1/providers/availability`.

### Fixed

- **Merge Registration Import:** Corrected `server.py` to import `register_client_recognition_tool` from its dedicated `client_recognition` module after merging the department tool branch.

### Client Recognition Response Mapping

- **fix:** The MCP tool maps lead responses such as `{"name":"SK"}` to `{"client_name":"SK"}`, preserves null results, and returns `client_metadata` (`ai_summaries`, `custom_fields`).
- **fix:** The lead lookup uses the `phone_number` query parameter (`GET /v1/webhooks/mcp/lead?org_id={org_id}&phone_number={phone}`, 5s timeout).

### Fixed (docs only, no code changes)

- Added missing `Features/Client Recognition Tool.md` and `Features/Org Processes Tool.md`.
- Refreshed `Home.md`, `Architecture/Overview.md`, `Architecture/APIs.md`, `Architecture/Security & Auth.md`, `Context/Repository Map.md`, `Context/Stack.md`, `Knowledge/Conventions.md` to match the working tree at `993b674`.
- Recorded known drift: missing `docker-compose.yml`, missing `tests/` suite, `tools/__init__.py` export gap, `pyproject.toml` version drift (`0.1.0` vs `0.3.3`), stale `Greeting Tool.md`.

## [0.3.3] - 2026-09-07

### Added

- **Inbound Client Recognition Tool (`recognize_client`)**: Added an MCP tool that normalizes an inbound phone number, sends `org_id` and the E.164-style number to `GET /v1/webhooks/mcp/lead`, and returns lead data or `null` for anonymous callers.
- **Bounded Backend Lookup**: Client recognition uses a five-second backend timeout and fails open so inbound calls are not blocked when the backend is unavailable.

## [0.3.2] - 2026-09-01

### Fixed

- **Production Dockerfile Python Interpreter Binding**: Fixed `exec /app/.venv/bin/livekit-mcp: no such file or directory` error caused by `apt-get install python3-dev` creating a virtual environment bound to `/usr/bin/python3.11` instead of the base image's `/usr/local/bin/python3.12`. Configured `UV_PYTHON=/usr/local/bin/python3.12` and `--python /usr/local/bin/python3.12` flags in `Dockerfile`.
- **Docker Compose Environment & Database Mapping**: Added root `docker-compose.yml` with `env_file: .env`, mapping `AUTH_SERVER_URL=${AUTH_SERVER_URL}`, correcting `DATABASE_URL` format to `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres-mcp:5432/${POSTGRES_DB}`, and stripping invalid quotes.

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
