# LiveKit MCP Server

<div align="center">

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![MCP](https://img.shields.io/badge/protocol-MCP%202.0-orange.svg)](https://modelcontextprotocol.io/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**A high-performance Model Context Protocol (MCP 2.0) Server bridging AI Agents and Backend Services with the MantraCare LiveKit Voice & Telephony Engine.**

[Architecture](#-system-architecture) •
[Quick Start](#-quick-start) •
[Configuration](#-configuration) •
[Tools](#-available-tools) •
[Authentication](#-authentication) •
[Connecting Clients](#-connecting-mcp-clients) •
[Development](#-development)

</div>

---

## 📖 Overview

The **LiveKit MCP Server** acts as the central intelligence and scheduling hub. It connects backend databases (`MantraAssist-backend`), telephony voice agents (`~/lkt`), and OAuth security (`~/mantra-auth`), providing AI agents with real-time tools for doctor availability, appointment scheduling, and caller timezone resolution.

### Key Capabilities

- 🚀 **MCP 2.0 Compliance**: Built on the official Python `mcp` SDK using Server-Sent Events (SSE) and Streamable HTTP transports (`/sse`, `/messages`, `/api/tools/call`).
- 🌍 **International Timezone Auto-Detection**: Automatically detects caller country and IANA timezone from international phone numbers (`+1` US ➔ EDT/CDT, `+44` UK ➔ GMT/BST, `+91` India ➔ IST, `+971` UAE ➔ GST) using Google's `phonenumbers` engine, converting UTC database slots to local time on the fly.
- 👨‍⚕️ **Multi-Provider Schedules**: Handles arrays of doctors/providers and their respective available working hours in a single request.
- 🔐 **OAuth 2.1 & Shared JWT Security**: Native HS256 JWT validation compatible with `mantra-auth`, supporting both `Authorization: Bearer <token>` headers and `?token=<token>` query parameters.
- ⚡ **Lightning Fast Async Core**: Powered by Starlette, `asyncpg` connection pooling, and Uvicorn.
- 🧠 **Agentic Memory**: Permanent Obsidian knowledge vault (`obsidian/`) and `AGENTS.md` rules.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. mantra-auth (:3000)                                                      │
│    Next.js OAuth 2.1 Authorization Server                                   │
│    • DB: postgres_auth (:5441 / mantra_auth_dev)                            │
│    • Issues HS256 JWT Tokens for Clients & Services                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Issues JWT Bearer Token
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. MantraAssist-backend (:5500) [MCP CLIENT]                                │
│    Express.js / TypeScript Core Backend                                     │
│    • Computes doctor working hours from assist_db                           │
│    • Calls MCP tool over SSE / HTTP (/sse?token=...)                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Invokes `receive_doctor_availability`
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. livekit-mcp (:8000) [THIS MCP SERVER]                                    │
│    Starlette + MCP 2.0 SSE Transport                                        │
│    • Auth Middleware: Validates HS256 JWT                                   │
│    • Timezone Resolver: Detects caller timezone from phone number           │
│    • Formatter: Normalizes UTC slots ➔ Caller's localized 12-hour format    │
│    • Public Endpoints: /health, /                                           │
│    • Protected Endpoints: /sse, /messages, /api/tools/call                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Real-time Tool Result
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. lkt (:8081) [VOICE TELEPHONY AGENT]                                      │
│    MantraCare LiveKit Voice Telephony Engine                                │
│    • STT ➔ LLM ➔ TTS Voice Pipeline                                         │
│    • Calls check_doctor_availability dynamically mid-call                   │
│    • Speaks localized doctor times naturally to the caller                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Layout

```text
livekit-mcp/
├── .env.example                # Sample environment variables
├── .gitignore                  # Git ignore definitions
├── .python-version             # Python version pin (3.11)
├── AGENTS.md                   # Agent Memory instructions
├── dev.sh                      # Development startup script
├── pyproject.toml              # UV package specification & build settings
├── uv.lock                     # Deterministic lockfile
├── README.md                   # Project documentation
│
├── obsidian/                   # Permanent Agentic Knowledge Base
│   ├── Home.md                 # Project navigation hub
│   ├── Architecture/           # System design, data flow, security & APIs
│   ├── Context/                # Stack, project summary & repository map
│   ├── Development/            # Sprint tracking, TODO & Changelog
│   ├── Features/               # Feature specifications (tools, auth)
│   └── Knowledge/              # Coding standards & conventions
│
├── scripts/
│   └── generate_token.py       # CLI utility to generate signed JWT tokens
│
└── src/
    └── livekit_mcp/
        ├── __init__.py
        ├── config.py           # Pydantic Settings & environment validation
        ├── server.py           # MCPServer & Starlette app factory
        ├── main.py             # CLI runner with Uvicorn
        ├── auth/
        │   ├── __init__.py
        │   ├── jwt.py          # HS256 JWT decoding & claims validation
        │   └── middleware.py   # Pure ASGI auth middleware (headers & ?token=)
        ├── clients/
        │   ├── __init__.py
        │   ├── db_client.py    # Async PostgreSQL pool (asyncpg)
        │   ├── lkt_client.py   # Async HTTP client for lkt (:8081)
        │   └── auth_client.py  # Async HTTP client for mantra-auth (:3000)
        ├── utils/
        │   ├── __init__.py
        │   └── timezone.py     # Phone number timezone auto-detection & UTC converter
        └── tools/
            ├── __init__.py
            ├── greeting.py     # `greet_user` health test tool
            ├── providers.py    # `search_provider_availability` direct DB search
            └── doctor_availability.py # `receive_doctor_availability` receiver tool
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python**: 3.11 or higher
- **uv**: Fast Python package manager ([Install uv](https://docs.astral.sh/uv/getting-started/installation/))
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Installation & Configuration

```bash
cd ~/livekit-mcp
cp .env.example .env
uv sync
```

### 3. Generate a JWT Access Token

To generate a signed 72-hour access token for testing or client configuration:

```bash
uv run python scripts/generate_token.py --hours 72
```

### 4. Start the Server

```bash
./dev.sh
```

Server runs at `http://localhost:8000`.

---

## 🛠 Available Tools

### 1. `receive_doctor_availability`
Receives calculated doctor availability and open time slots in **UTC** for multiple providers. Automatically detects the caller's timezone from their international phone number and returns formatted local times for the voice agent.

* **Arguments**:
  - `org_id` *(int)*: Organization ID.
  - `date` *(string)*: Target date (`YYYY-MM-DD`).
  - `caller_phone` *(string, optional)*: International phone number (`+12025550123`, `+918360625862`).
  - `providers` *(array of objects)*:
    - `user_id` *(int)*: Doctor ID (`users.id`).
    - `name` *(string)*: Doctor's name.
    - `available_slots` *(array of strings)*: UTC time ranges (`["14:00 - 15:00", "16:00 - 17:00"]`).

* **Example Payload**:
```json
{
  "org_id": 66,
  "date": "2026-08-25",
  "caller_phone": "+12025550123",
  "providers": [
    {
      "user_id": 12,
      "name": "Dr. Ananya Sharma",
      "available_slots": [
        "14:00 - 15:00",
        "16:00 - 17:00"
      ]
    },
    {
      "user_id": 15,
      "name": "Dr. Rajesh Kumar",
      "available_slots": [
        "15:00 - 16:00",
        "17:00 - 18:00"
      ]
    }
  ]
}
```

* **Voice Agent Output**:
```text
📅 Available Doctors on Tuesday, Aug 25, 2026 (Local Timezone: America/New_York):

1. Dr. Ananya Sharma (User ID: 12)
   • Available Slots: 10:00 AM – 11:00 AM EDT, 12:00 PM – 1:00 PM EDT

2. Dr. Rajesh Kumar (User ID: 15)
   • Available Slots: 11:00 AM – 12:00 PM EDT, 1:00 PM – 2:00 PM EDT

Org ID: 66 | Caller Phone: +12025550123
```

---

### 2. `search_provider_availability`
Queries `assist_db` directly (`asyncpg`), evaluates RFC 5545 recurrence rules, and converts working hours to the organization's or caller's local timezone.

* **Arguments**:
  - `org_id` *(int)*: Organization ID.
  - `query_date` *(string)*: Date to search (`YYYY-MM-DD`).
  - `query` *(string, optional)*: Doctor name or specialty filter.
  - `caller_phone` *(string, optional)*: Caller phone number for timezone localization.

---

### 3. `greet_user`
Simple latency and connectivity verification tool.

---

## 🌐 API Endpoints

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| **`/health`** | `GET` | Public | Returns service status, version, and auth configuration |
| **`/`** | `GET` | Public | Root welcome & discovery info |
| **`/sse`** | `GET` | Bearer / `?token=` | MCP Server-Sent Events connection stream |
| **`/messages`** | `POST` | Bearer / `?token=` | MCP JSON-RPC message transport |
| **`/api/tools/call`** | `POST` | Bearer / `?token=` | Direct tool execution endpoint for microservices |

---

## 🔐 Authentication

All protected endpoints (`/sse`, `/messages`, `/api/tools/call`) require a valid JWT token signed with `JWT_SECRET`.

### Passing the Token:
1. **Via Authorization Header**:
   ```http
   Authorization: Bearer <YOUR_JWT_TOKEN>
   ```
2. **Via Query Parameter** *(Recommended for EventSource browser/SSE clients)*:
   ```http
   GET http://localhost:8000/sse?token=<YOUR_JWT_TOKEN>
   ```

---

## 🛠 Connecting MCP Clients

### From Node.js / TypeScript (`MantraAssist-backend`):
```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const transport = new SSEClientTransport(
  new URL(`http://localhost:8000/sse?token=${process.env.MCP_JWT_TOKEN}`)
);
const client = new Client({ name: "mantra-backend", version: "1.0.0" }, { capabilities: {} });
await client.connect(transport);

const result = await client.callTool({
  name: "receive_doctor_availability",
  arguments: { ... }
});
```

---

## 💻 Development

- **Lint & Format**:
  ```bash
  uv run ruff check --fix .
  uv run ruff format .
  ```
- **Token Generation**:
  ```bash
  uv run python scripts/generate_token.py --user "test-agent" --hours 24
  ```
