"""Unit tests for JWT handling and authentication middleware."""

from livekit_mcp.auth.jwt import (
    JWTPayload,
    decode_jwt_token,
    verify_jwt_token,
)
from livekit_mcp.config import Settings


def test_jwt_verification_success(test_settings: Settings, valid_token: str):
    """Test successful verification of a valid token."""
    payload = verify_jwt_token(
        token=valid_token,
        secret=test_settings.jwt_secret,
        algorithm=test_settings.jwt_algorithm,
    )
    assert payload is not None
    assert payload.sub == "test-agent-123"
    assert payload.name == "Test Agent"
    assert payload.has_scope("telephony:call") is True
    assert payload.has_scope("admin:write") is False


def test_jwt_verification_expired(test_settings: Settings, expired_token: str):
    """Test verification failure on expired token."""
    payload = verify_jwt_token(
        token=expired_token,
        secret=test_settings.jwt_secret,
    )
    assert payload is None


def test_jwt_verification_invalid_secret(test_settings: Settings, valid_token: str):
    """Test verification failure with wrong secret key."""
    payload = verify_jwt_token(
        token=valid_token,
        secret="wrong-secret-key-that-is-at-least-32-chars-long",
    )
    assert payload is None


def test_jwt_decode_unverified(valid_token: str):
    """Test unverified decoding."""
    payload = decode_jwt_token(valid_token)
    assert payload is not None
    assert payload.sub == "test-agent-123"


def test_jwt_payload_scope_helper():
    """Test scope helper method on JWTPayload."""
    payload = JWTPayload(sub="user-1", scope="read write delete")
    assert payload.has_scope("read") is True
    assert payload.has_scope("write") is True
    assert payload.has_scope("admin") is False

    empty_payload = JWTPayload(sub="user-2", scope="")
    assert empty_payload.has_scope("read") is False
