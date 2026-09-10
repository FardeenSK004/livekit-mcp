# Current Sprint

> **Sprint:** 0.3.0 Production Dockerization & Org Processes Integration  
> **Last Updated:** 2026-09-10  
> **Status:** Active
> **HEAD:** `0de282c` (Merge tool/department into feature/mcp-client, 2026-09-09)

## Repo-State Sync (2026-09-10, no code changes)
- [x] **Vault resync:** Added `Features/Department Discovery Tool.md`; rewrote `Features/Doctor Availability Receiver Tool.md` to the live signature (pre-supplied slots OR backend query + DB fallback); corrected `Features/Client Recognition Tool.md` (metadata + `phone_number` param); fixed `Features/Org Processes Tool.md` fallback chain to `/v1/...`; fixed `Architecture/APIs.md` + `Security & Auth.md` route prefixes (`/tools/call`, `/dev/*`); refreshed `Home.md`, `Architecture/Overview.md`, `Context/Repository Map.md`, `Knowledge/Conventions.md` to HEAD `0de282c`.
- [ ] **Gap: `docker-compose.yml` missing** — sprint/Changelog 0.3.2 reference it, but it is not tracked in git nor on disk. Re-add or correct history.
- [ ] **Gap: `tests/` suite missing** — earlier docs claim 27 passing tests; no `tests/` dir exists (only `.pytest_cache`). Re-scaffold suite.
- [ ] **Gap: `tools/__init__.py` exports** — `register_client_recognition_tool` + `register_department_tool` are wired in `server.py` but not re-exported. Add to `__all__`.
- [ ] **Gap: version drift** — `pyproject.toml` is `0.1.0`, Changelog tracks `0.3.3`. Bump to `0.3.3`.
- [ ] **Stale: `Greeting Tool.md`** — describes `greet_user`, but no `greeting.py` module exists in `tools/` (no references in `src/`). Confirm removal or restore.
- [ ] **Stale: `README.md`** — documents `/sse?token=...`, `/api/tools/call`, repo layout without `department_list.py`/`client_recognition.py`, and 3 tools. Refresh to `/tools/call`, 6 tool names, current layout.

## Completed (2026-09-09, post-`993b674`)

- [x] **Department Discovery Tool (2026-09-09):** Added `get_org_departments` (`tools/department_list.py` + `MantraAssistBackendClient.get_org_departments()` → `GET /v1/webhooks/mcp/departments`) with 10-min TTL cache and tolerant payload normalization. Registered in `server.py`. Commits `a11f3f4` + merge `0de282c`.
- [x] **Client Recognition Metadata (2026-09-09):** `recognize_client` now returns `client_metadata.{ai_summaries, custom_fields}` unwrapping `data`/`result` envelopes with `name`/`full_name` fallbacks. Commit `7d88c33`.
- [x] **Route Prefix Simplification (2026-09-09):** `routes/api.py` mounts `/tools/call` + `/dev/*` (was `/api/tools/call`, `/api/dev/*`). Part of `a11f3f4`.
- [x] **LKT Active-Calls Path Fix (2026-09-09):** `lkt_client.get_active_calls()` now hits `/v1/dashboard/active-calls` (was `/api/v1/...`). Part of `a11f3f4`.
- [x] **Doctor Availability Endpoint Rename (2026-09-09):** description now references `/v1/providers/availability` (was `/api/v1/...`). Part of `a11f3f4`.

## Completed

- [x] **Inbound Client Recognition MCP Tool (2026-09-07):** Added `recognize_client` to normalize the inbound caller number and query the MA backend with `org_id` plus phone number. The livekit agent calls this tool before greeting and treats `null`, timeout, or backend failure as an anonymous caller. Backend endpoint contract (current): `GET /v1/webhooks/mcp/lead?org_id={org_id}&phone_number={phone}`.

- [x] **Production Docker Build & Exec Fix (2026-09-01):** Resolved `exec /app/.venv/bin/livekit-mcp: no such file or directory` by enforcing `UV_PYTHON=/usr/local/bin/python3.12` in `Dockerfile`. Added `docker-compose.yml` with `env_file: .env` and fixed `DATABASE_URL` format.
- [x] **Production Environment Config (2026-08-30):** Created dedicated production environment file `.env.prod` with `ENVIRONMENT=production`, secure JWT secret configuration, and production service URLs. Files: `.env.prod`.
- [x] **Production Multi-Stage Dockerfile (2026-08-29):** Created production Dockerfile using `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, unprivileged `appuser` (UID 10001), layer caching, runtime healthcheck, and direct binary CMD execution. Files: `Dockerfile`.
- [x] **Organization Processes & Stages Tool (`fetch_org_processes`) (2026-08-27):** Implemented `fetch_org_processes` (and alias `receive_org_processes`) with 10-min in-memory TTL caching querying `MantraAssist-backend`. Files: `src/livekit_mcp/tools/org_processes.py`, `src/livekit_mcp/clients/backend_client.py`.
- [x] **Doctor `provider_user_id` Injection (2026-08-27):** Added doctor user IDs into `receive_doctor_availability` output for automatic post-call appointment resolution. Files: `src/livekit_mcp/tools/doctor_availability.py`.
- [x] **Unauthenticated Backend Client (2026-08-27):** Removed `x-client-id` and `x-client-secret` headers from `MantraAssistBackendClient`. Files: `src/livekit_mcp/clients/backend_client.py`.
- [x] **JSON Root Status Endpoint (2026-08-27):** Replaced static landing page with lightweight JSON response. Files: `src/livekit_mcp/routes/api.py`.
- [x] **Agentic Memory Infrastructure (2026-08-20):** Created `AGENTS.md` and full Obsidian knowledge vault (`obsidian/`) replicating the agentic memory pattern from `~/lkt`.
- [x] **Shared JWT Authentication (2026-08-20):** Implemented HS256 JWT validation and pure ASGI middleware supporting header and query parameter token injection compatible with `mantra-auth`.
- [x] **MCP Server Core & SSE Transport (2026-08-20):** Set up `MCPServer` with `/sse`, `/messages`, `/health`, and `/api/tools/call` endpoints.
- [x] **Greeting Test Tool (2026-08-20):** Implemented typed, documented `greet_user` tool for end-to-end verification.
- [x] **Provider Availability Search Tool (2026-08-21):** Implemented `search_provider_availability` tool in `src/livekit_mcp/tools/providers.py` with direct PostgreSQL connection pool (`DatabaseClient`), UTC-to-local timezone conversion (`zoneinfo.ZoneInfo`), and RFC 5545 recurrence rule matching against `assist_db`.
- [x] **Doctor Availability Receiver Tool (2026-08-22):** Implemented `receive_doctor_availability` tool in `src/livekit_mcp/tools/doctor_availability.py` receiving computed slots from `MantraAssist-backend` supporting arrays of providers.
- [x] **International Timezone Resolution (2026-08-22):** Integrated Google's `phonenumbers` engine (`src/livekit_mcp/utils/timezone.py`) to auto-detect caller country/timezone from phone number (`+1` US -> EDT, `+44` UK -> GMT/BST, `+91` India -> IST, `+971` UAE -> GST, `+61` Australia -> AEST) and convert UTC slots dynamically.
- [x] **Integration Contract (`structure.json` & `format.json`) (2026-08-22):** Created minimal 1:1 schema contracts for backend developer.
- [x] **Automated Test Suite (2026-08-22):** 27 unit & integration tests passing 100% across auth, config, greeting, provider search, doctor availability receiver, and international timezone conversions.
- [x] **Developer Landing Dashboard & Diagnostics UI (2026-08-25):** Created a clean, simplified developer landing console at `/` with PostgreSQL/LKT diagnostics and dynamic tool catalog schemas.
- [x] **Department Clarification Tool (2026-09-09):** Added `get_org_departments` with 10-minute in-memory caching, registered it in the MCP server, and normalized the MantraAssist payload as `{org_id, departments}` for broad-symptom clarification.
- [x] **Merge Import Repair (2026-09-10):** Corrected the client recognition registration import to use `tools.client_recognition` after merging the department tool branch.

