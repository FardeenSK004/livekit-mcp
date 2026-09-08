# Technology Stack

## Core Technologies

| Technology | Purpose |
| :--- | :--- |
| **Python 3.11+** | Runtime environment |
| **uv** | Modern, fast package and project manager |
| **mcp (1.2.x)** | Pinned Model Context Protocol SDK (`mcp[cli]>=1.2.0,<1.3.0`, FastMCP) |
| **Starlette** | High-performance ASGI framework for SSE and HTTP routing |
| **Uvicorn** | Production-ready lightning-fast ASGI server |
| **PyJWT (with Cryptography)** | HS256 JWT decoding & verification |
| **Pydantic / Pydantic Settings** | Type validation and environment management |
| **HTTPX** | Async HTTP client for inter-service communication |
| **asyncpg** | Async PostgreSQL driver + pool (`DatabaseClient`, telemetry logger) |
| **phonenumbers** | Google libphonenumber engine for caller country/timezone detection |
| **Pytest & Pytest-Asyncio** | Automated unit & integration testing framework (suite currently missing — see Repository Map) |
| **Ruff** | Ultra-fast linter and code formatter |
| **Docker (uv:python3.12-bookworm-slim)** | Production multi-stage image, non-root `appuser` (UID 10001) |
