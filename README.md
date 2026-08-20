# LiveKit MCP Server

<div align="center">

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![MCP](https://img.shields.io/badge/protocol-MCP%202.0-orange.svg)](https://modelcontextprotocol.io/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)]()

**A high-performance Model Context Protocol (MCP 2.0) Server bridging AI Agents with the MantraCare LiveKit Voice & Telephony Engine.**

[Architecture](#-system-architecture) •
[Quick Start](#-quick-start) •
[Configuration](#-configuration) •
[Connecting Clients](#-connecting-mcp-clients) •
[Authentication](#-authentication) •
[Tools](#-available-tools) •
[Development](#-development--testing)

</div>

---

## 📖 Overview

The **LiveKit MCP Server** allows LLMs and AI coding assistants (such as Antigravity, Claude, Cursor, and custom agents) to securely control, inspect, and trigger voice telephony pipelines powered by **LiveKit** (`~/lkt`) and authenticated via **Mantra Auth** (`~/mantra-auth`).

### Key Capabilities
- 🚀 **MCP 2.0 Compliance**: Built on the official Python `mcp` SDK using Server-Sent Events (SSE) and Streamable HTTP transports.
- 🔐 **OAuth 2.1 & Shared JWT Security**: Native HS256 JWT validation matching `mantra-auth`, with support for both `Authorization: Bearer` headers and `?token=` query parameters.
- ⚡ **Lightning Fast Async Core**: Powered by Starlette, Uvicorn, and `uv` package management.
- 🧩 **Modular Tool Architecture**: Domain-separated tools for telephony, call analytics, knowledge base search, and SIP trunking.
- 🧠 **Agentic Memory**: Full Obsidian knowledge base (`obsidian/`) and `AGENTS.md` rules for AI pair programming context preservation.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ AI Client (Cursor / Claude / Antigravity / Web Agent)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ 1. Bearer Token / ?token= (OAuth 2.1)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [3. mantra-auth (:3000)]                                    │
│ Next.js + Prisma OAuth 2.1 Authorization Server             │
│ - Issues HS256 JWTs and verifies via /api/oauth/introspect  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Shared JWT Secret Verification
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [2. livekit-mcp (:8000)] (This Server)                      │
│ - Starlette ASGI + MCP 2.0 SSE Transport                    │
│ - Pure ASGI Auth Middleware (HS256 JWT validation)          │
│ - Public Endpoints: /health, /                              │
│ - Protected Endpoints: /sse, /messages                      │
│ - Registered Tools: greet_user, [Telephony/KB/SIP coming]   │
└──────────────────────────────┬──────────────────────────────┘
                               │ 2. Async HTTP (REST)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [1. lkt (:8081)]                                            │
│ MantraCare LiveKit Voice Agent & Telephony Engine           │
│ - SIP Trunks (Plivo, Zadarma, VoiceLink, Twilio)            │
│ - LiveKit Cloud WebRTC Rooms & STT→LLM→TTS Voice Pipeline   │
│ - PostgreSQL (call_logs, kb_pages) & Redis (queues, locks)  │
└─────────────────────────────────────────────────────────────┘
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
│   └── Knowledge/              # Coding standards & architectural conventions
│
├── src/
│   └── livekit_mcp/
│       ├── __init__.py
│       ├── config.py           # Pydantic Settings & environment validation
│       ├── server.py           # MCPServer & Starlette app factory
│       ├── main.py             # CLI runner with Uvicorn
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt.py          # HS256 JWT decoding & claims validation
│       │   └── middleware.py   # Pure ASGI auth middleware (headers & ?token=)
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── lkt_client.py   # Async HTTP client for lkt FastAPI (:8081)
│       │   └── auth_client.py  # Async HTTP client for mantra-auth (:3000)
│       └── tools/
│           ├── __init__.py
│           └── greeting.py     # Initial `greet_user` verification tool
│
└── tests/
    ├── __init__.py
    ├── conftest.py             # Fixtures for tokens, settings & test client
    ├── test_config.py          # Configuration unit tests
    ├── test_auth.py            # JWT verification & claims unit tests
    ├── test_greeting.py        # Tool registration & execution tests
    └── test_server.py          # Endpoints, SSE & Auth integration tests
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python**: 3.11 or higher
- **uv**: Fast Python package manager ([Install uv](https://docs.astral.sh/uv/getting-started/installation/))
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Installation & Setup

1. **Clone the repository and enter the directory**:
   ```bash
   cd ~/livekit-mcp
   ```

2. **Create your environment configuration**:
   ```bash
   cp .env.example .env
   ```

3. **Install dependencies with `uv`**:
   ```bash
   uv sync
   ```

### 3. Running the Server

Start the development server with auto-reload:
```bash
./dev.sh
```

Or run directly using `uv`:
```bash
uv run python -m livekit_mcp.main
```

The server will be available at **`http://localhost:8000`**.

---

## ⚙️ Configuration

All settings are managed in `src/livekit_mcp/config.py` using `pydantic-settings` and loaded from `.env`:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `HOST` | string | `0.0.0.0` | Server bind address |
| `PORT` | integer | `8000` | Server listening port |
| `ENVIRONMENT` | string | `development` | `development`, `test`, or `production` |
| `LOG_LEVEL` | string | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `AUTH_ENABLED` | boolean | `true` | Enforce JWT authentication on protected endpoints |
| `JWT_SECRET` | string | `your-super-secret-...` | Shared secret key for HS256 JWT signature verification |
| `JWT_ALGORITHM` | string | `HS256` | JWT signing algorithm (matches `mantra-auth`) |
| `AUTH_SERVER_URL` | string | `http://localhost:3000` | Base URL of the Mantra Auth server |
| `JWT_ISSUER` | string | `http://localhost:3000` | Expected JWT issuer claim (`iss`) |
| `JWT_AUDIENCE` | string | *(empty)* | Optional expected audience claim (`aud`) |
| `LKT_API_BASE_URL` | string | `http://localhost:8081` | Base URL of the LKT Voice Agent API |
| `LKT_API_TIMEOUT` | float | `15.0` | HTTP request timeout in seconds for LKT calls |
| `LIVEKIT_URL` | string | *(empty)* | Direct LiveKit Cloud WebSocket URL (optional) |
| `LIVEKIT_API_KEY` | string | *(empty)* | Direct LiveKit Cloud API Key (optional) |
| `LIVEKIT_API_SECRET` | string | *(empty)* | Direct LiveKit Cloud API Secret (optional) |

---

## 📡 Endpoints

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| **`/health`** | `GET` | ❌ No | Public health & readiness check returning service status |
| **`/`** | `GET` | ❌ No | Service status and endpoint metadata |
| **`/sse`** | `GET` | ✅ Yes | Opens a persistent Server-Sent Events (SSE) stream for MCP clients |
| **`/messages`** | `POST` | ✅ Yes | JSON-RPC 2.0 endpoint for MCP requests (tool execution, listings) |

### Health Check Sample
```bash
curl http://localhost:8000/health
```
```json
{
  "status": "healthy",
  "service": "livekit-mcp",
  "version": "0.1.0",
  "auth_enabled": true,
  "environment": "development",
  "lkt_api_configured": true,
  "timestamp": "2026-08-20T12:30:00.000000+00:00"
}
```

---

## 🔐 Authentication

The server implements **OAuth 2.1 / HS256 Shared JWT Authentication** compatible with `mantra-auth`.

### Supplying Credentials

1. **Authorization Header (Standard)**:
   ```http
   GET /sse HTTP/1.1
   Host: localhost:8000
   Authorization: Bearer <your-jwt-access-token>
   ```

2. **Query Parameter (For SSE / EventSource clients)**:
   ```http
   GET /sse?token=<your-jwt-access-token> HTTP/1.1
   Host: localhost:8000
   ```

### Expected JWT Claims
```json
{
  "sub": "user-123",
  "aud": "client-app",
  "iss": "http://localhost:3000",
  "exp": 1755694800,
  "iat": 1755691200,
  "scope": "openid profile telephony:call",
  "token_type": "access_token"
}
```

> **Development Tip**: Set `AUTH_ENABLED=false` in `.env` to disable token verification during local testing.

---

## 🛠️ Available Tools

### 1. `greet_user`
A verification tool that validates MCP connectivity, parameter parsing, and server status.

* **Parameters**:
  * `name` (string, required): Name of the user or agent invoking the tool.
  * `message` (string, optional): Custom greeting message.
* **Returns**:
  ```text
  👋 Hello, Alice!

  Welcome to MantraCare LiveKit MCP!

  --- System Status ---
  • Service: LiveKit MCP Server
  • Status: Operational & Ready
  • Timestamp: 2026-08-20T12:30:00.000000+00:00
  • Protocol: MCP 2.0 (SSE / HTTP)
  ```

---

## 🔌 Connecting MCP Clients

### 1. Antigravity / Gemini CLI (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "livekit": {
      "serverUrl": "http://localhost:8000/sse"
    }
  }
}
```

### 2. Cursor IDE (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "livekit": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "Authorization": "Bearer <YOUR_JWT_TOKEN>"
      }
    }
  }
}
```

### 3. Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "livekit": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/fardeen/livekit-mcp",
        "run",
        "python",
        "-m",
        "livekit_mcp.main"
      ],
      "env": {
        "AUTH_ENABLED": "false"
      }
    }
  }
}
```

---

## 🧪 Development & Testing

### Running Tests
The project includes a comprehensive test suite covering configuration, JWT verification, middleware, and tools:
```bash
uv run pytest -v
```

### Code Formatting & Linting
Enforce clean coding standards using `ruff`:
```bash
# Check code
uv run ruff check .

# Auto-fix issues & format
uv run ruff check --fix .
uv run ruff format .
```

### Adding New Tools
To add a new tool to `livekit-mcp`:
1. Create a module in `src/livekit_mcp/tools/<domain>.py`.
2. Define a registration function:
   ```python
   from mcp.server.mcpserver import MCPServer

   def register_telephony_tools(server: MCPServer) -> None:
       @server.tool(name="trigger_call", description="Trigger an outbound call")
       async def trigger_call(phone_number: str, prompt: str) -> str:
           # Call LktClient here
           return f"Call initiated to {phone_number}"
   ```
3. Register the function in `src/livekit_mcp/server.py` inside `create_mcp_server()`.
4. Add unit tests in `tests/test_<domain>.py`.

---

## 📚 Agentic Memory

This repository adheres to the **Agentic Memory** pattern. Before making architectural changes, review the Obsidian knowledge vault at `obsidian/`:
- `obsidian/Home.md` — Project navigation hub
- `obsidian/Architecture/Overview.md` — System design & topology
- `obsidian/Development/Current Sprint.md` — Active development status
- `obsidian/Development/TODO.md` — Upcoming roadmap
- `obsidian/Knowledge/Coding Standards.md` — Code conventions

---

## 📄 License

Proprietary © MantraCare. All rights reserved.
