# Current Sprint

> **Sprint:** 0.1.0 Initial Setup & Doctor Availability  
> **Last Updated:** 2026-08-22  
> **Status:** Active

- [x] **Project Scaffolding (2026-08-20):** Structured project using Python 3.11+ and `uv`, configured `pyproject.toml` with build backend, dev dependencies, `ruff`, and `pytest`.
- [x] **Agentic Memory Infrastructure (2026-08-20):** Created `AGENTS.md` and full Obsidian knowledge vault (`obsidian/`) replicating the agentic memory pattern from `~/lkt`.
- [x] **Shared JWT Authentication (2026-08-20):** Implemented HS256 JWT validation and pure ASGI middleware supporting header and query parameter token injection compatible with `mantra-auth`.
- [x] **MCP Server Core & SSE Transport (2026-08-20):** Set up `MCPServer` with `/sse`, `/messages`, `/health`, and `/api/tools/call` endpoints.
- [x] **Greeting Test Tool (2026-08-20):** Implemented typed, documented `greet_user` tool for end-to-end verification.
- [x] **Provider Availability Search Tool (2026-08-21):** Implemented `search_provider_availability` tool in `src/livekit_mcp/tools/providers.py` with direct PostgreSQL connection pool (`DatabaseClient`), UTC-to-local timezone conversion (`zoneinfo.ZoneInfo`), and RFC 5545 recurrence rule matching against `assist_db`.
- [x] **Doctor Availability Receiver Tool (2026-08-22):** Implemented `receive_doctor_availability` tool in `src/livekit_mcp/tools/doctor_availability.py` receiving computed slots from `MantraAssist-backend` supporting arrays of providers.
- [x] **International Timezone Resolution (2026-08-22):** Integrated Google's `phonenumbers` engine (`src/livekit_mcp/utils/timezone.py`) to auto-detect caller country/timezone from phone number (`+1` US -> EDT, `+44` UK -> GMT/BST, `+91` India -> IST, `+971` UAE -> GST, `+61` Australia -> AEST) and convert UTC slots dynamically.
- [x] **Integration Contract (`structure.json` & `format.json`) (2026-08-22):** Created minimal 1:1 schema contracts for backend developer.
- [x] **Automated Test Suite (2026-08-22):** 27 unit & integration tests passing 100% across auth, config, greeting, provider search, doctor availability receiver, and international timezone conversions.
