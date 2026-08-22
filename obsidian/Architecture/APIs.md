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
- **Description:** Receives calculated doctor working hours, open slots, and booked slots pushed from MantraAssist backend and formats them into voice context for LiveKit Voice Agent calls.
- **Arguments:**
  - `doctor_id` (integer, required): Doctor ID from `users` table.
  - `doctor_name` (string, required): Full name of the doctor with title.
  - `date` (string, required): Date in `YYYY-MM-DD`.
  - `timezone` (string, required): Timezone string (e.g. `Asia/Kolkata`).
  - `available_slots` (array of strings, required): List of open slots in local time.
  - `specialization` (string, optional): Medical specialty.
  - `booked_slots` (array of strings, optional): Already booked slots.
  - `slot_interval_minutes` (integer, optional, default: 60): Duration in minutes.
  - `notes` (string, optional): Special clinical notes.
