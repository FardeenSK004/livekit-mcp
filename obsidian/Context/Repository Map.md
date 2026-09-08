# Repository Map

> **Last verified:** 2026-09-08 (against `git ls-files` + working tree)

```text
livekit-mcp/
├── .dockerignore               # Docker build exclusions
├── .env                        # Local runtime env (untracked)
├── .env.example                # Sample environment variables
├── .env.prod                   # Production env (ENVIRONMENT=production)
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version pin
├── AGENTS.md                   # Agent Memory instructions
├── Dockerfile                  # Production multi-stage build (uv, Python 3.12, appuser)
├── README.md                   # Developer and setup documentation
├── dev.sh                      # Local development runner
├── main.py                     # Top-level runner shim
├── pyproject.toml              # UV package spec (name livekit-mcp, version 0.1.0 — drift vs Changelog 0.3.3)
├── uv.lock                     # Locked dependencies
├── scripts/
│   └── generate_token.py       # HS256 JWT test-token generator CLI
├── src/
│   └── livekit_mcp/
│       ├── __init__.py
│       ├── config.py           # Pydantic Settings & environment validation
│       ├── server.py           # FastMCP + Starlette app builder (registers 4 tool modules)
│       ├── main.py             # CLI runner / Uvicorn entrypoint
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt.py          # JWT verification & payload model
│       │   └── middleware.py   # Pure-ASGI auth middleware (header + ?token=)
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── auth_client.py      # Mantra Auth RFC 7662 introspection
│       │   ├── backend_client.py   # MantraAssist-backend (availability, processes, recognition)
│       │   ├── db_client.py        # asyncpg pool for assist_db
│       │   └── lkt_client.py       # Async client for LKT FastAPI service
│       ├── routes/
│       │   ├── __init__.py
│       │   └── api.py          # /health, / root JSON, /api/tools/call, /api/dev/*
│       ├── tools/
│       │   ├── __init__.py             # Exports provider/doctor/processes registrars (client_recognition NOT re-exported)
│       │   ├── providers.py            # search_provider_availability
│       │   ├── doctor_availability.py  # receive_doctor_availability
│       │   ├── org_processes.py        # fetch_org_processes + alias receive_org_processes
│       │   └── client_recognition.py   # recognize_client
│       └── utils/
│           ├── db_logger.py    # MCP event telemetry (save_mcp_event, get_recent_events)
│           └── timezone.py     # phonenumbers caller-tz detection + UTC conversion
└── obsidian/                   # Agentic memory knowledge base
    ├── Home.md
    ├── Architecture/
    │   ├── Overview.md
    │   ├── Data Flow.md
    │   ├── Security & Auth.md
    │   └── APIs.md
    ├── Context/
    │   ├── Project Summary.md
    │   ├── Stack.md
    │   └── Repository Map.md
    ├── Development/
    │   ├── Current Sprint.md
    │   ├── TODO.md
    │   └── Changelog.md
    ├── Features/
    │   ├── Greeting Tool.md
    │   ├── Provider Availability Tool.md
    │   ├── Doctor Availability Receiver Tool.md
    │   ├── Org Processes Tool.md
    │   └── Client Recognition Tool.md
    └── Knowledge/
        ├── Coding Standards.md
        └── Conventions.md
```

## Known Drift (2026-09-08)
- `docker-compose.yml` (sprint/Changelog 0.3.2) is **missing** from repo — needs re-adding or history correction.
- `tests/` suite no longer exists — only `.pytest_cache` remains.
- No `greeting.py` — `Greeting Tool.md` describes a tool with no current source module.
