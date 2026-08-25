"""Server factory and application builder for LiveKit MCP Server."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route

from livekit_mcp.auth.middleware import AuthMiddleware
from livekit_mcp.config import Settings, get_settings
from livekit_mcp.tools.doctor_availability import register_doctor_availability_tool
from livekit_mcp.tools.greeting import register_greeting_tool
from livekit_mcp.tools.providers import register_provider_tools

logger = logging.getLogger(__name__)

# Track server startup time for dashboard uptime display
STARTUP_TIME = datetime.now(UTC)


def mask_url(url: str) -> str:
    """Mask password or credentials in connection URL strings for security."""
    if not url:
        return ""
    if "@" in url and "://" in url:
        try:
            scheme, rest = url.split("://", 1)
            credentials, host_db = rest.rsplit("@", 1)
            if ":" in credentials:
                user, _ = credentials.split(":", 1)
                return f"{scheme}://{user}:••••••••@{host_db}"
        except Exception:
            pass
    return url


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

    # Root status endpoint serving HTML dashboard
    async def root_endpoint(request: Request) -> HTMLResponse:
        try:
            template_path = Path(__file__).parent / "templates" / "dashboard.html"
            with open(template_path, encoding="utf-8") as f:
                template = f.read()
        except Exception as e:
            logger.error("Failed to load dashboard HTML template: %s", e)
            return HTMLResponse("<h1>Error: Could not load dashboard template</h1>", status_code=500)

        # Get list of tools
        tools = await server.list_tools()
        tools_list = []
        for t in tools:
            tools_list.append({
                "name": t.name,
                "description": t.description,
                "inputSchema": t.inputSchema
            })

        # Prepare replacements
        replacements = {
            "{{ENVIRONMENT}}": app_settings.environment,
            "{{HOST}}": request.url.hostname or app_settings.host,
            "{{PORT}}": str(request.url.port or app_settings.port),
            "{{PROJECT_DIR}}": str(Path(__file__).parent.parent.parent.resolve()),
            "{{JWT_SECRET}}": app_settings.jwt_secret,
            "{{DATABASE_URL}}": mask_url(app_settings.effective_db_url),
            "{{STARTUP_TIME}}": STARTUP_TIME.isoformat(),
            "{{TOOLS_JSON}}": json.dumps(tools_list),
        }

        content = template
        for k, v in replacements.items():
            content = content.replace(k, v)

        return HTMLResponse(content)

    # Dev token generator endpoint
    async def dev_token_endpoint(request: Request) -> JSONResponse:
        if app_settings.is_production:
            return JSONResponse(
                {"status": "error", "message": "Token generation is disabled in production"},
                status_code=403
            )

        try:
            body = await request.json()
            user_id = body.get("user", "admin-user-id")
            client_id = body.get("client", "test-client-id")
            scope = body.get("scope", "mcp:all")
            hours = int(body.get("hours", 24))
        except Exception:
            user_id = "admin-user-id"
            client_id = "test-client-id"
            scope = "mcp:all"
            hours = 24

        try:
            import uuid
            from datetime import timedelta

            import jwt

            now = datetime.now(UTC)
            exp = now + timedelta(hours=hours)
            payload = {
                "sub": user_id,
                "aud": client_id,
                "iss": app_settings.auth_server_url,
                "iat": int(now.timestamp()),
                "exp": int(exp.timestamp()),
                "scope": scope,
                "token_type": "access_token",
                "jti": uuid.uuid4().hex[:16],
            }
            token = jwt.encode(payload, app_settings.jwt_secret, algorithm=app_settings.jwt_algorithm)
            return JSONResponse({
                "status": "success",
                "token": token,
                "claims": {
                    "sub": user_id,
                    "aud": client_id,
                    "scope": scope,
                    "hours": hours
                }
            })
        except Exception as e:
            logger.error("Failed to generate dev token: %s", e)
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    # Database connection test endpoint
    async def check_db_endpoint(request: Request) -> JSONResponse:
        from livekit_mcp.clients.db_client import DatabaseClient
        db_client = DatabaseClient(app_settings)
        try:
            pool = await db_client.get_pool()
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return JSONResponse({"status": "healthy", "message": "Database connection successful"})
        except Exception as e:
            logger.error("Database connection check failed: %s", e)
            return JSONResponse({"status": "unhealthy", "message": str(e)}, status_code=500)

    # LKT voice agent engine ping endpoint
    async def check_lkt_endpoint(request: Request) -> JSONResponse:
        import httpx
        url = app_settings.lkt_api_base_url
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
                return JSONResponse({
                    "status": "healthy" if response.status_code < 500 else "unhealthy",
                    "code": response.status_code,
                    "message": f"Service responded with status {response.status_code}"
                })
        except Exception as e:
            logger.error("LKT Service ping failed: %s", e)
            return JSONResponse({"status": "unhealthy", "message": str(e)}, status_code=500)

    # Direct tool call endpoint for legacy compatibility
    async def call_tool_endpoint(request: Request) -> JSONResponse:
        try:
            body = await request.json()
            tool_name = body.get("name")
            arguments = body.get("arguments", {})

            if not tool_name:
                return JSONResponse({"status": "error", "message": "Missing tool name"}, status_code=400)

            result = await server.call_tool(name=tool_name, arguments=arguments)
            
            if hasattr(result, "content"):
                output_text = "\n".join(c.text for c in result.content if hasattr(c, "text"))
            elif isinstance(result, list):
                output_text = "\n".join(c.text for c in result if hasattr(c, "text"))
            else:
                output_text = str(result)
                
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
        Route("/api/dev/token", endpoint=dev_token_endpoint, methods=["POST"]),
        Route("/api/dev/check-db", endpoint=check_db_endpoint, methods=["GET"]),
        Route("/api/dev/check-lkt", endpoint=check_lkt_endpoint, methods=["GET"]),
    ]

    app = Starlette(routes=routes)

    # Add AuthMiddleware
    app.add_middleware(AuthMiddleware, settings=app_settings)

    return app
