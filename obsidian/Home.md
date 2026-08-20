# LiveKit MCP Server — Knowledge Base

> **Version:** 0.1.0  
> **Package:** `livekit-mcp`  
> **Repository:** `livekit-mcp`  
> **Language & Runtime:** Python 3.11+ / uv  
> **Protocol:** Model Context Protocol (MCP 2.0)  
> **Last Updated:** 2026-08-20

---

## Quick Links

| Area | Document |
| :--- | :--- |
| 🏛️ Architecture | [[Architecture/Overview.md\|Overview]] · [[Architecture/Data Flow.md\|Data Flow]] · [[Architecture/Security & Auth.md\|Security & Auth]] · [[Architecture/APIs.md\|APIs]] |
| 🎯 Features | [[Features/Greeting Tool.md\|Greeting Tool]] |
| 📋 Development | [[Development/Current Sprint.md\|Current Sprint]] · [[Development/TODO.md\|TODO]] · [[Development/Changelog.md\|Changelog]] |
| 🧠 Knowledge | [[Knowledge/Coding Standards.md\|Coding Standards]] · [[Knowledge/Conventions.md\|Conventions]] |
| 📖 Context | [[Context/Project Summary.md\|Project Summary]] · [[Context/Stack.md\|Stack]] · [[Context/Repository Map.md\|Repository Map]] |

---

## Project Identity

**LiveKit MCP Server** is a high-performance Model Context Protocol (MCP) server built with Python and `uv`. It serves as the intelligent AI interface bridging external AI agents (Claude, Cursor, Antigravity, custom agents) with the **MantraCare LiveKit Voice & Telephony Engine** (`~/lkt`) and the **Mantra Auth OAuth 2.1 Server** (`~/mantra-auth`).

## Architecture Snapshot

```
AI Client (Cursor / Claude / Web)
       │ (Authorization: Bearer <JWT>)
       ▼
[LiveKit MCP Server (:8000)]
  ├── Auth Layer (Shared JWT & Mantra-Auth Introspection)
  ├── Starlette SSE / HTTP Transport (/sse, /messages)
  └── MCP Server & Tools
       │ (REST / Webhooks)
       ▼
[LKT Voice Agent Engine (:8081)]
```

---

## Repository Status

- **Transport:** SSE & Streamable HTTP (`/sse`, `/messages`), with Starlette integration
- **Auth:** OAuth 2.1 / HS256 Shared JWT Verification against `mantra-auth`
- **Testing:** Comprehensive automated pytest test suite (`tests/`)
- **Package Manager:** `uv`
