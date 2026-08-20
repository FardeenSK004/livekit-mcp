# Project Summary

## Executive Summary
`livekit-mcp` is a Model Context Protocol (MCP) server designed to expose the MantraCare LiveKit Voice & Telephony Engine (`~/lkt`) to AI models and developer tooling.

## Key Objectives
1. **Security:** Native integration with `mantra-auth` via OAuth 2.1 / HS256 shared JWT verification.
2. **Performance:** Asynchronous, low-latency SSE / HTTP transports with Starlette and Uvicorn.
3. **Modularity:** Clean separation of concerns with domain-based tool modules.
4. **Developer Experience:** Modern Python package management via `uv`, agentic memory documentation in `obsidian/`, and automated testing.
