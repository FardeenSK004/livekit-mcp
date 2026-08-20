# Repository Map

```text
livekit-mcp/
├── .env.example                # Sample environment variables
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version pin (3.11)
├── AGENTS.md                   # Agent Memory instructions
├── dev.sh                      # Local development runner
├── pyproject.toml              # UV package specification
├── README.md                   # Developer and setup documentation
├── obsidian/                   # Agentic memory knowledge base
│   ├── Home.md
│   ├── Architecture/
│   │   ├── Overview.md
│   │   ├── Data Flow.md
│   │   ├── Security & Auth.md
│   │   └── APIs.md
│   ├── Context/
│   │   ├── Project Summary.md
│   │   ├── Stack.md
│   │   └── Repository Map.md
│   ├── Development/
│   │   ├── Current Sprint.md
│   │   ├── TODO.md
│   │   └── Changelog.md
│   ├── Features/
│   │   └── Greeting Tool.md
│   └── Knowledge/
│       ├── Coding Standards.md
│       └── Conventions.md
├── src/
│   └── livekit_mcp/
│       ├── __init__.py
│       ├── config.py           # Pydantic Settings & environment validation
│       ├── server.py           # MCPServer and Starlette application builder
│       ├── main.py             # CLI runner / Uvicorn server entrypoint
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt.py          # JWT verification & payload model
│       │   └── middleware.py   # Starlette auth middleware
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── lkt_client.py   # Async client for LKT FastAPI service
│       │   └── auth_client.py  # Async client for Mantra Auth introspection
│       └── tools/
│           ├── __init__.py
│           └── greeting.py     # Greeting & verification tool
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures and mock tokens
    ├── test_config.py          # Configuration unit tests
    ├── test_auth.py            # Authentication & JWT unit tests
    ├── test_greeting.py        # Greeting tool unit tests
    └── test_server.py          # Server & SSE integration tests
```
