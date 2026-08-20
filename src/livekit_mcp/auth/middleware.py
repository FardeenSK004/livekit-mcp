"""ASGI authentication middleware for LiveKit MCP Server."""

import logging

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from livekit_mcp.auth.jwt import JWTPayload, verify_jwt_token
from livekit_mcp.config import Settings

logger = logging.getLogger(__name__)

# Paths that bypass authentication
DEFAULT_PUBLIC_PATHS: set[str] = {
    "/health",
    "/",
    "/docs",
    "/openapi.json",
    "/favicon.ico",
}


class AuthMiddleware:
    """Pure ASGI middleware enforcing JWT verification on protected endpoints."""

    def __init__(
        self,
        app: ASGIApp,
        settings: Settings,
        public_paths: set[str] | None = None,
    ):
        self.app = app
        self.settings = settings
        self.public_paths = public_paths or DEFAULT_PUBLIC_PATHS

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process incoming ASGI request through JWT verification."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Allow public paths without authentication
        if path in self.public_paths:
            await self.app(scope, receive, send)
            return

        # Skip auth if disabled in settings
        if not self.settings.auth_enabled:
            self._inject_auth_state(
                scope,
                JWTPayload(sub="anonymous-dev", scope="all"),
            )
            await self.app(scope, receive, send)
            return

        # Extract token from header or query param
        request = Request(scope, receive)
        token = self._extract_token(request)

        if not token:
            logger.warning("Unauthorized request to %s: Missing token", path)
            response = JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "error_description": "Authorization token required (via Bearer header or ?token= query param)",
                },
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )
            await response(scope, receive, send)
            return

        # Verify token
        payload = verify_jwt_token(
            token=token,
            secret=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            issuer=self.settings.jwt_issuer,
            audience=self.settings.jwt_audience,
        )

        if not payload:
            logger.warning("Unauthorized request to %s: Invalid or expired token", path)
            response = JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_token",
                    "error_description": "Token is invalid, malformed, or expired",
                },
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )
            await response(scope, receive, send)
            return

        # Attach auth payload to ASGI scope state
        self._inject_auth_state(scope, payload)
        await self.app(scope, receive, send)

    def _inject_auth_state(self, scope: Scope, payload: JWTPayload) -> None:
        """Inject verified payload into ASGI scope state."""
        state = scope.setdefault("state", {})
        state["auth"] = payload
        state["user_id"] = payload.sub

    def _extract_token(self, request: Request) -> str | None:
        """Extract JWT token from Authorization header or query parameters."""
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:].strip()

        # Query param fallback for EventSource / SSE clients
        query_token = request.query_params.get("token")
        if query_token:
            return query_token.strip()

        return None
