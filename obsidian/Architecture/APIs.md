# API & Protocol Endpoints

## Endpoints

### 1. `GET /health`
- **Auth:** None (Public)
- **Description:** Health and readiness check endpoint.
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "livekit-mcp",
    "version": "0.1.0",
    "auth_enabled": true,
    "lkt_api_configured": true
  }
  ```

### 2. `GET /sse`
- **Auth:** Bearer token in header or `?token=<jwt>`
- **Description:** Opens Server-Sent Events stream for MCP client communication. Returns the `/messages` URI for subsequent RPC requests.

### 3. `POST /messages`
- **Auth:** Bearer token in header or `?token=<jwt>`
- **Description:** JSON-RPC 2.0 endpoint for MCP commands (tool listing, tool execution, prompts, resources).

### 4. `GET /` (Root Status)
- **Auth:** None (Public)
- **Description:** Lightweight JSON status response (`{"status": "working", "service": "livekit-mcp", ...}`).

### 5. `POST /tools/call`
- **Auth:** Bearer token required
- **Description:** Direct synchronous tool invocation for internal microservices (e.g. `lkt`). Body: `{"name": "<tool>", "arguments": {...}}`. Handles both FastMCP `CallToolResult` and raw list responses; logs start/complete/fail telemetry via `db_logger`.

### 6. Dev & Diagnostics (public, token generator disabled in production)
- `POST /dev/token` — signs local HS256 test JWTs (`user`, `client`, `scope`, `hours`); returns `403` in production.
- `GET /dev/check-db` — verifies PostgreSQL connectivity (`SELECT 1`).
- `GET /dev/check-lkt` — pings the LKT voice engine base URL.
- `GET /dev/recent-events` — returns last 30 telemetry events from `db_logger`.

---

## Registered MCP Tools

### `greet_user`
- **Description:** Formats a welcome message and returns system status for the caller.
- **Arguments:**
  - `name` (string, required): The name of the user or agent.
  - `message` (string, optional): An optional custom greeting message.

### `search_provider_availability`
- **Description:** Queries `assist_db` (`provider_availability` + `providers` + `provider_to_organization`) and returns available doctors, working hours converted to local timezone (IST), and remaining capacity for an organization on a specific date.
- **Arguments:**
  - `org_id` (integer, required): Organization ID (e.g. 66).
  - `query_date` (string, required): Date in format `YYYY-MM-DD` (e.g. `2026-08-25`).
  - `query` (string, optional): Optional doctor name or specialization filter (e.g. `Sharma`, `Diabetes`, `Cardiology`).

### `receive_doctor_availability`
- **Description:** Resolves doctor working hours and open slots for an organization and formats them into voice-agent-ready local-time strings. Accepts pre-supplied `providers` / `name`+`available_slots`, otherwise queries `MantraAssist-backend` (`GET /v1/webhooks/mcp`, `POST` fallback) with a direct `assist_db` fallback. Timezone: explicit `timezone` → phone detection → `Asia/Kolkata`; UTC slots localized via `convert_utc_slot_to_local`.
- **Arguments:**
  - `org_id` (integer|string, optional): Organization ID.
  - `name` (string, optional): Doctor name filter.
  - `date` (string, optional): Target date (`YYYY-MM-DD`, `today`, `tomorrow`, ...).
  - `department` (string, optional): Department / specialization filter.
  - `providers` (array of objects, optional): Pre-supplied providers (`user_id`, `name`, `available_slots` UTC ranges).
  - `available_slots` (array of strings, optional): Pre-supplied UTC slots for `name` (+ `user_id`).
  - `caller_phone` (string, optional): Caller number for timezone auto-detection.
  - `timezone` (string, optional): Explicit timezone override.
- **Backend contract:** fixed UTC schema `{org_id, date, datetime, doc_name, department, caller_phone}`.

### `fetch_org_processes` (+ alias `receive_org_processes`)
- **Description:** Queries `MantraAssist-backend` for all processes and stage IDs with descriptions for an organization; used during post-call analysis to assign `process_id` / `new_stage_id`. 10-minute in-memory TTL cache per `org_id`, with fallback endpoint chain.
- **Arguments:**
  - `org_id` (integer|string, required): Organization ID (e.g. `77`).

### `recognize_client`
- **Description:** Identifies an inbound caller by organization and phone number before greeting. Normalizes the number to E.164 style (bare 10-digit numbers assumed `+91`), calls `GET /v1/webhooks/mcp/lead?org_id={org_id}&phone_number={phone}` with a 5s timeout, and fails open (`{"client_name": null, "client_metadata": {"ai_summaries": [], "custom_fields": []}}`) on timeout/non-200/backend failure.
- **Arguments:**
  - `org_id` (integer|string, required): Organization ID for the inbound number.
  - `phone_number` (string, required): Inbound caller number, preferably E.164.

### `get_org_departments`
- **Description:** Fetches the medical departments/specialties supported by an organization from `MantraAssist-backend` (`GET /v1/webhooks/mcp/departments?org_id={org_id}`); used for one clarifying question on broad symptoms before doctor-availability lookup. 10-minute in-memory TTL cache per `org_id`; returns `{"org_id": <id>, "departments": [<names>]}` (empty list on failure).
- **Arguments:**
  - `org_id` (integer|string, required): Organization ID for the current call.
