"""Unit tests for configuration settings."""

from livekit_mcp.config import Settings, get_settings


def test_default_settings():
    """Verify default settings values."""
    settings = Settings()
    assert settings.port == 8000
    assert settings.jwt_algorithm == "HS256"
    assert settings.auth_enabled is True
    assert settings.lkt_api_base_url == "http://localhost:8081"
    assert settings.is_production is False


def test_custom_settings():
    """Verify custom settings overrides."""
    settings = Settings(
        HOST="10.0.0.1",
        PORT=9000,
        ENVIRONMENT="production",
        AUTH_ENABLED=False,
        JWT_SECRET="custom-secret",
    )
    assert settings.host == "10.0.0.1"
    assert settings.port == 9000
    assert settings.is_production is True
    assert settings.auth_enabled is False
    assert settings.jwt_secret == "custom-secret"


def test_cached_settings():
    """Verify get_settings returns singleton."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
