"""Pytest configuration and shared fixtures for LiveKit MCP Server."""

import pytest
from starlette.testclient import TestClient

from livekit_mcp.auth.jwt import create_jwt_token
from livekit_mcp.config import Settings
from livekit_mcp.server import create_app

TEST_SECRET = "test-secret-key-for-unit-testing-32-chars-long"


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings with predictable credentials."""
    return Settings(
        host="127.0.0.1",
        port=8000,
        environment="test",
        auth_enabled=True,
        jwt_secret=TEST_SECRET,
        jwt_algorithm="HS256",
        auth_server_url="http://localhost:3000",
        lkt_api_base_url="http://localhost:8081",
    )


@pytest.fixture
def valid_token(test_settings: Settings) -> str:
    """Generate a valid signed JWT access token for testing."""
    payload = {
        "sub": "test-agent-123",
        "aud": "test-client",
        "scope": "openid profile telephony:call",
        "name": "Test Agent",
        "email": "agent@mantracare.com",
    }
    return create_jwt_token(
        payload=payload,
        secret=test_settings.jwt_secret,
        expires_in=3600,
        issuer=test_settings.auth_server_url,
    )


@pytest.fixture
def expired_token(test_settings: Settings) -> str:
    """Generate an expired signed JWT access token for testing."""
    payload = {
        "sub": "expired-agent",
        "aud": "test-client",
        "scope": "basic",
    }
    return create_jwt_token(
        payload=payload,
        secret=test_settings.jwt_secret,
        expires_in=-300,  # Expired 5 minutes ago
        issuer=test_settings.auth_server_url,
    )


@pytest.fixture
def test_client(test_settings: Settings) -> TestClient:
    """Provide a Starlette TestClient with auth enabled."""
    app = create_app(settings=test_settings)
    return TestClient(app)


@pytest.fixture
def no_auth_test_client(test_settings: Settings) -> TestClient:
    """Provide a Starlette TestClient with auth disabled."""
    settings = test_settings.model_copy(update={"auth_enabled": False})
    app = create_app(settings=settings)
    return TestClient(app)
