# LiveKit MCP Server

> Model Context Protocol (MCP 2.0) Server for LiveKit Voice Agent and Telephony Services.

The **LiveKit MCP Server** enables AI agents (Claude, Cursor, Antigravity, custom agents) to securely interact with the MantraCare LiveKit Voice Engine (`~/lkt`) and authenticate against the Mantra Auth OAuth 2.1 Server (`~/mantra-auth`).

---

## 🏛️ System Architecture

```
┌──────────────────────────────────────────────┐
│  AI Agent / MCP Client (Cursor, Claude, etc) │
└──────────────────────┬───────────────────────┘
                       │ 1. Bearer Token / ?token= (OAuth 2.1)
                       ▼
┌──────────────────────────────────────────────┐
│  LiveKit MCP Server (:8000)                  │
│  ├── Starlette SSE / HTTP Transport          │
│  ├── HS256 JWT Authentication Layer          │
│  ├── /health (Public Readiness Check)        │
│  └── MCP Server & Tools                      │
│       └── greet_user (Initial Tool)          │
└──────────────────────┬───────────────────────┘
                       │ 2. Async REST API Calls
                       ▼
┌──────────────────────────────────────────────┐
│  LKT Voice Agent Engine (:8081)              │
│  (Telephony, LiveKit Rooms, Call Logs, KB)   │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Setup Environment
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Run the Server
```bash
# Using dev script
./dev.sh

# Or directly with uv
uv run python -m livekit_mcp.main
```

The server starts at `http://localhost:8000`.

---

## 📡 Endpoints

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | ❌ No | Health and readiness check |
| `/` | `GET` | ❌ No | Server status & endpoints info |
| `/sse` | `GET` | ✅ Yes | Opens SSE stream for MCP client |
| `/messages` | `POST` | ✅ Yes | JSON-RPC 2.0 MCP message endpoint |

---

## 🔐 Authentication

Authentication is handled via **HS256 Shared JWT** compatible with `mantra-auth`:

* **Header:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
* **Query Parameter:** `?token=<JWT_ACCESS_TOKEN>` (supported for EventSource SSE connections)

To disable authentication for local testing, set `AUTH_ENABLED=false` in `.env`.

---

## 🛠️ Registered Tools

### `greet_user`
Greets a user or agent and returns system status and current UTC timestamp.
* **Arguments:**
  * `name` (string, required): Name of the caller.
  * `message` (string, optional): Custom message text.

---

## 🧪 Testing & Quality

Run the test suite:
```bash
uv run pytest -v
```

Run linter & code formatter:
```bash
uv run ruff check .
uv run ruff format .
```

---

## 📚 Agentic Memory

This repository maintains a permanent Obsidian knowledge base in `obsidian/` and follows the guidelines in `AGENTS.md`.
