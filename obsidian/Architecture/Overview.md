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
| **Auth Client** | `src/livekit_mcp/clients/auth_client.py` | Async HTTP client for `mantra-auth` OAuth introspection |
| **Tools** | `src/livekit_mcp/tools/` | Modular MCP tool definitions (greeting, calls, logs, KB, etc.) |

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
│            ├── greet_user (Initial verification tool)         │
│            └── [Future: Telephony, KB, Logs, SIP]            │
└──────────────────────────────┬───────────────────────────────┘
                               │ Async HTTP (REST)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ LKT Telephony & Voice Agent Engine (FastAPI on :8081)        │
└──────────────────────────────────────────────────────────────┘
```
