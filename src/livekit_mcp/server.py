"""Server factory and application builder for LiveKit MCP Server."""

import logging
from datetime import UTC, datetime

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from livekit_mcp.auth.middleware import AuthMiddleware
from livekit_mcp.config import Settings, get_settings
from livekit_mcp.tools.greeting import register_greeting_tool

logger = logging.getLogger(__name__)


def create_mcp_server(settings: Settings | None = None) -> MCPServer:
    """Create and configure the underlying MCP server instance."""
    server = MCPServer(
        name="livekit-mcp",
        version="0.1.0",
        instructions=(
            "LiveKit MCP Server provides tools to interact with the MantraCare "
            "voice agent engine, telephony trunks, call logs, and knowledge base."
        ),
    )

    # Register initial tools
    register_greeting_tool(server)

    return server


def create_app(settings: Settings | None = None) -> Starlette:
    """Create the full Starlette application with SSE transport and auth middleware."""
    app_settings = settings or get_settings()
    server = create_mcp_server(app_settings)

    # Configure transport security allowing local, test, and configured hosts
    transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=app_settings.is_production,
        allowed_hosts=[
            "127.0.0.1:*",
            "localhost:*",
            "[::1]:*",
            "testserver",
            "testserver:*",
            f"{app_settings.host}:*",
        ],
        allowed_origins=[
            "http://127.0.0.1:*",
            "http://localhost:*",
            "http://[::1]:*",
            "http://testserver",
            "http://testserver:*",
        ],
    )

    # Build base MCP Starlette application with transport security
    app = server.sse_app(transport_security=transport_security)

    # Health check route
    async def health_endpoint(request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "healthy",
                "service": "livekit-mcp",
                "version": "0.1.0",
                "auth_enabled": app_settings.auth_enabled,
                "environment": app_settings.environment,
                "lkt_api_configured": bool(app_settings.lkt_api_base_url),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    # Root status endpoint
    async def root_endpoint(request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "message": "LiveKit MCP Server is running",
                "docs": "/health",
                "sse_endpoint": "/sse",
                "messages_endpoint": "/messages",
            }
        )

    # Add custom routes
    app.add_route("/health", health_endpoint, methods=["GET"])
    app.add_route("/", root_endpoint, methods=["GET"])

    # Add AuthMiddleware
    app.add_middleware(AuthMiddleware, settings=app_settings)

    return app
