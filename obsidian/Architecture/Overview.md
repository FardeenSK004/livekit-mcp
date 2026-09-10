# Architecture Overview

## Pattern

Modular, asynchronous, service-oriented architecture using Python `asyncio`, `Starlette`, `Pydantic Settings`, and the official `mcp` SDK (v2).

## Core Components

| Module | File | Role |
| :--- | :--- | :--- |
| **Server Builder** | `src/livekit_mcp/server.py` | Initializes `MCPServer`, mounts tools, creates Starlette app with routes & middleware |
| **Auth Middleware** | `src/livekit_mcp/auth/middleware.py` | Intercepts HTTP requests, validates JWT tokens or query param tokens |
| **JWT Validator** | `src/livekit_mcp/auth/jwt.py` | Decodes & verifies HS256 signatures with `JWT_SECRET` |
| **Settings** | `src/livekit_mcp/config.py` | Pydantic Settings loading environment variables |
| **LKT Client** | `src/livekit_mcp/clients/lkt_client.py` | Async HTTP client for communicating with `lkt` FastAPI service |
| **Auth Client** | `src/livekit_mcp/clients/auth_client.py` | Async HTTP client for `mantra-auth` OAuth introspection (RFC 7662) |
| **Backend Client** | `src/livekit_mcp/clients/backend_client.py` | Async HTTP client for `MantraAssist-backend` (availability, org processes, client recognition; unauthenticated, `ngrok-skip-browser-warning` header) |
| **Database Client** | `src/livekit_mcp/clients/db_client.py` | `asyncpg` connection pool for `assist_db` provider lookups |
| **API Routes** | `src/livekit_mcp/routes/api.py` | Health, root JSON status, `/tools/call`, dev diagnostics (`check-db`, `check-lkt`, `token`, `recent-events`) |
| **Telemetry** | `src/livekit_mcp/utils/db_logger.py` | Fire-and-forget MCP event logging (`save_mcp_event`, `get_recent_events`) + in-memory buffer |
| **Timezone Utils** | `src/livekit_mcp/utils/timezone.py` | `phonenumbers`-based caller timezone detection, date resolution, UTC conversion |
| **Tools** | `src/livekit_mcp/tools/` | Modular MCP tool definitions (providers, doctor availability, org processes, client recognition, departments) |

## Topology

```
┌──────────────────────────────────────────────────────────────┐
│ MCP Client (AI Model, IDE, Antigravity, Cursor, Web)         │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP / SSE + Bearer Token
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ LiveKit MCP Server (Starlette + MCP 2.0 on :8000)            │
│  ├── Authentication Middleware (HS256 Shared JWT / Auth API) │
│  ├── /health (Readiness / Liveness Check)                    │
│  ├── /sse (Server-Sent Events connection)                    │
│  └── /messages (JSON-RPC 2.0 message handler)                │
│       └── Tool Manager                                       │
│            ├── search_provider_availability (assist_db direct) │
│            ├── receive_doctor_availability (backend push/query)│
│            ├── fetch_org_processes (+ alias receive_org_processes) │
│            ├── get_org_departments (department discovery)      │
│            └── recognize_client (inbound caller recognition)   │
└──────────────────────────────┬───────────────────────────────┘
                                │ Async HTTP (REST)
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ MantraAssist-backend (HTTP API on :5500)                     │
│  ├── GET+POST /v1/webhooks/mcp (availability, UTC schema)    │
│  ├── GET /v1/webhooks/mcp/departments (departments)          │
│  ├── GET /v1/webhooks/mcp/processes (org processes, + fallbacks) │
│  └── GET /v1/webhooks/mcp/lead?org_id={org_id}&phone_number={phone} │
└──────────────────────────────┬───────────────────────────────┘
                               │ Async HTTP (REST)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ LKT Telephony & Voice Agent Engine (FastAPI on :8081)        │
└──────────────────────────────────────────────────────────────┘
```
