import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from livekit_mcp.config import Settings
from livekit_mcp.utils.db_logger import save_mcp_event

logger = logging.getLogger(__name__)

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

def get_api_routes(server: FastMCP, app_settings: Settings, startup_time: datetime) -> list[Route]:
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
            template_path = Path(__file__).parent.parent / "templates" / "dashboard.html"
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
            "{{PROJECT_DIR}}": str(Path(__file__).parent.parent.parent.parent.resolve()),
            "{{JWT_SECRET}}": app_settings.jwt_secret,
            "{{DATABASE_URL}}": mask_url(app_settings.effective_db_url),
            "{{STARTUP_TIME}}": startup_time.isoformat(),
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

            import asyncio
            asyncio.create_task(
                save_mcp_event(
                    event_type="tool_execution_started",
                    event_source="call_tool_endpoint",
                    event_payload={"tool_name": tool_name, "arguments": arguments},
                    call_id=arguments.get("call_id", "")
                )
            )

            result = await server.call_tool(name=tool_name, arguments=arguments)
            
            if hasattr(result, "content"):
                output_text = "\n".join(c.text for c in result.content if hasattr(c, "text"))
            elif isinstance(result, list):
                output_text = "\n".join(c.text for c in result if hasattr(c, "text"))
            else:
                output_text = str(result)
                
            asyncio.create_task(
                save_mcp_event(
                    event_type="tool_execution_completed",
                    event_source="call_tool_endpoint",
                    event_payload={"tool_name": tool_name, "result": output_text[:1000]},
                    event_status="success",
                    call_id=arguments.get("call_id", "")
                )
            )

            return JSONResponse({"status": "success", "result": output_text})
        except Exception as e:
            logger.error("Error executing tool in call_tool_endpoint: %s", e)
            import asyncio
            asyncio.create_task(
                save_mcp_event(
                    event_type="tool_execution_failed",
                    event_source="call_tool_endpoint",
                    event_payload={"tool_name": body.get("name") if 'body' in locals() else "unknown"},
                    event_status="failed",
                    event_error=str(e),
                )
            )
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    return [
        Route("/health", endpoint=health_endpoint, methods=["GET"]),
        Route("/", endpoint=root_endpoint, methods=["GET"]),
        Route("/api/tools/call", endpoint=call_tool_endpoint, methods=["POST"]),
        Route("/api/dev/token", endpoint=dev_token_endpoint, methods=["POST"]),
        Route("/api/dev/check-db", endpoint=check_db_endpoint, methods=["GET"]),
        Route("/api/dev/check-lkt", endpoint=check_lkt_endpoint, methods=["GET"]),
    ]
