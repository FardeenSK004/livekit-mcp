"""Integration and unit tests for server endpoints and authentication middleware."""

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from livekit_mcp.auth.middleware import AuthMiddleware
from livekit_mcp.config import Settings


def test_health_endpoint_public(test_client: TestClient):
    """Verify health endpoint is accessible without authentication."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "livekit-mcp"
    assert data["auth_enabled"] is True


def test_root_endpoint_public(test_client: TestClient):
    """Verify root status endpoint is accessible without authentication."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "LiveKit MCP Server" in data["message"]


def test_protected_endpoint_unauthorized_without_token(test_client: TestClient):
    """Verify protected endpoints reject requests lacking credentials with 401."""
    response = test_client.post("/messages", json={"jsonrpc": "2.0"})
    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "unauthorized"


def test_protected_endpoint_unauthorized_with_expired_token(
    test_client: TestClient, expired_token: str
):
    """Verify protected endpoints reject expired tokens with 401."""
    response = test_client.post(
        "/messages",
        headers={"Authorization": f"Bearer {expired_token}"},
        json={"jsonrpc": "2.0"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "invalid_token"


def test_protected_endpoint_authorized_with_bearer_token(test_client: TestClient, valid_token: str):
    """Verify valid Bearer token passes auth middleware."""
    # When token is valid, auth middleware passes request down to /messages
    response = test_client.post(
        "/messages",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"jsonrpc": "2.0"},
    )
    # The request passed auth (not 401). /messages will return its standard response (e.g. 400 for missing session or 200/404)
    assert response.status_code != 401


def test_protected_endpoint_authorized_with_query_param(test_client: TestClient, valid_token: str):
    """Verify valid token in query param (?token=) passes auth middleware."""
    response = test_client.post(
        f"/messages?token={valid_token}",
        json={"jsonrpc": "2.0"},
    )
    assert response.status_code != 401


def test_middleware_injects_auth_state(test_settings: Settings, valid_token: str):
    """Verify AuthMiddleware injects parsed JWTPayload into request state."""
    captured_state = {}

    async def mock_endpoint(request: Request) -> JSONResponse:
        captured_state["user_id"] = request.state.user_id
        captured_state["auth"] = request.state.auth
        return JSONResponse({"status": "ok"})

    from starlette.applications import Starlette
    from starlette.routing import Route

    app = Starlette(routes=[Route("/test-protected", mock_endpoint, methods=["GET"])])
    app.add_middleware(AuthMiddleware, settings=test_settings)

    client = TestClient(app)

    # 1. Without token -> 401
    res = client.get("/test-protected")
    assert res.status_code == 401

    # 2. With token -> 200 and state is populated
    res = client.get("/test-protected", headers={"Authorization": f"Bearer {valid_token}"})
    assert res.status_code == 200
    assert captured_state["user_id"] == "test-agent-123"
    assert captured_state["auth"].name == "Test Agent"


def test_middleware_when_auth_disabled(test_settings: Settings):
    """Verify AuthMiddleware injects anonymous dev user when auth is disabled."""
    captured_state = {}

    async def mock_endpoint(request: Request) -> JSONResponse:
        captured_state["user_id"] = request.state.user_id
        return JSONResponse({"status": "ok"})

    from starlette.applications import Starlette
    from starlette.routing import Route

    settings = test_settings.model_copy(update={"auth_enabled": False})
    app = Starlette(routes=[Route("/test-protected", mock_endpoint, methods=["GET"])])
    app.add_middleware(AuthMiddleware, settings=settings)

    client = TestClient(app)
    res = client.get("/test-protected")
    assert res.status_code == 200
    assert captured_state["user_id"] == "anonymous-dev"
