"""Server factory and application builder for LiveKit MCP Server."""

from datetime import UTC, datetime
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from livekit_mcp.auth.middleware import AuthMiddleware
from livekit_mcp.config import Settings, get_settings
from livekit_mcp.tools.doctor_availability import register_doctor_availability_tool
from livekit_mcp.tools.greeting import register_greeting_tool
from livekit_mcp.tools.providers import register_provider_tools

logger = logging.getLogger(__name__)


def create_mcp_server(settings: Settings | None = None) -> FastMCP:
    """Create and configure the underlying FastMCP server instance."""
    app_settings = settings or get_settings()

    server = FastMCP(
        name="livekit-mcp",
        instructions=(
            "LiveKit MCP Server provides tools to interact with the MantraCare "
            "voice agent engine, telephony trunks, call logs, knowledge base, "
            "and healthcare provider availability schedules."
        ),
    )

    # Register tools
    register_greeting_tool(server)
    register_provider_tools(server, settings=app_settings)
    register_doctor_availability_tool(server)

    return server


def create_app(settings: Settings | None = None) -> Starlette:
    """Create the full Starlette application with official SSE transport and auth middleware."""
    app_settings = settings or get_settings()
    server = create_mcp_server(app_settings)

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await server._mcp_server.run(
                read_stream,
                write_stream,
                server._mcp_server.create_initialization_options(),
            )
        return Response()

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
                "messages_endpoint": "/messages/",
                "protocol": "Model Context Protocol (JSON-RPC 2.0 / SSE)",
            }
        )

    # Direct tool call endpoint for legacy compatibility
    async def call_tool_endpoint(request: Request) -> JSONResponse:
        try:
            body = await request.json()
            tool_name = body.get("name")
            arguments = body.get("arguments", {})

            if not tool_name:
                return JSONResponse({"status": "error", "message": "Missing tool name"}, status_code=400)

            result = await server.call_tool(name=tool_name, arguments=arguments)
            output_text = "\n".join(c.text for c in result.content if hasattr(c, "text"))
            return JSONResponse({"status": "success", "result": output_text})
        except Exception as e:
            logger.error("Error executing tool in call_tool_endpoint: %s", e)
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    # Create Starlette app with routes & SSE transport mount
    routes = [
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse.handle_post_message),
        Route("/health", endpoint=health_endpoint, methods=["GET"]),
        Route("/", endpoint=root_endpoint, methods=["GET"]),
        Route("/api/tools/call", endpoint=call_tool_endpoint, methods=["POST"]),
    ]

    app = Starlette(routes=routes)

    # Add AuthMiddleware
    app.add_middleware(AuthMiddleware, settings=app_settings)

    return app
