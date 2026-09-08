# LiveKit MCP Server — Knowledge Base

> **Version:** 0.1.0  
> **Package:** `livekit-mcp`  
> **Repository:** `livekit-mcp`  
> **Language & Runtime:** Python 3.11+ / uv  
> **Protocol:** Model Context Protocol (MCP 2.0)  
> **Last Updated:** 2026-09-08

---

## Quick Links

| Area | Document |
| :--- | :--- |
| 🏛️ Architecture | [[Architecture/Overview.md\|Overview]] · [[Architecture/Data Flow.md\|Data Flow]] · [[Architecture/Security & Auth.md\|Security & Auth]] · [[Architecture/APIs.md\|APIs]] |
| 🎯 Features | [[Features/Greeting Tool.md\|Greeting Tool]] · [[Features/Provider Availability Tool.md\|Provider Availability]] · [[Features/Doctor Availability Receiver Tool.md\|Doctor Availability Receiver]] · [[Features/Org Processes Tool.md\|Org Processes]] · [[Features/Client Recognition Tool.md\|Client Recognition]] |
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
- **Auth:** OAuth 2.1 / HS256 Shared JWT Verification against `mantra-auth` (local verify first, RFC 7662 introspection fallback)
- **Registered Tools (5):** `search_provider_availability`, `receive_doctor_availability`, `fetch_org_processes` (+ alias `receive_org_processes`), `recognize_client`
- **Backends:** `MantraAssistBackendClient` (`MANTRAASSIST_BACKEND_URL`, default `:5500`) for availability, org processes, and client recognition; `LktClient` for voice engine (`:8081`); `AuthClient` for token introspection
- **Package Manager:** `uv`
- **Deploy:** Production multi-stage `Dockerfile` (Python 3.12, `appuser` UID 10001, `/health` healthcheck). Note: `docker-compose.yml` referenced in sprint history is not present in the repo as of 2026-09-08.
- **Testing:** `tests/` suite referenced in earlier docs no longer exists in the repo as of 2026-09-08 (only `.pytest_cache` remains) — suite needs re-scaffolding.
- **Version drift:** `pyproject.toml` still `0.1.0` while Changelog tracks `0.3.3` — version bump pending.
