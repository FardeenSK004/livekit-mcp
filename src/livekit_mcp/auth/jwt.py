"""JWT token verification and payload handling matching Mantra Auth."""

import logging
import time
from typing import Any

import jwt
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class JWTPayload(BaseModel):
    """Decoded JWT payload structure matching mantra-auth."""

    sub: str = Field(description="Subject (User ID or 'agent')")
    aud: str | None = Field(default=None, description="Audience (Client ID)")
    iss: str | None = Field(default=None, description="Issuer")
    iat: int | None = Field(default=None, description="Issued at timestamp")
    exp: int | None = Field(default=None, description="Expiration timestamp")
    scope: str | None = Field(default="", description="Space-separated scopes")
    token_type: str | None = Field(default="access_token", description="Token type")
    jti: str | None = Field(default=None, description="Unique JWT ID")
    name: str | None = Field(default=None, description="Subject display name")
    email: str | None = Field(default=None, description="Subject email")

    def has_scope(self, required_scope: str) -> bool:
        """Check if the payload contains a specific scope."""
        if not self.scope:
            return False
        scopes = set(self.scope.split())
        return required_scope in scopes


def verify_jwt_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
    issuer: str | None = None,
    audience: str | None = None,
) -> JWTPayload | None:
    """Verify and decode a JWT token using HS256 and shared secret.

    Args:
        token: Raw JWT string.
        secret: Shared HMAC secret key.
        algorithm: JWT signing algorithm (default HS256).
        issuer: Expected token issuer (optional).
        audience: Expected token audience (optional).

    Returns:
        JWTPayload if valid, None otherwise.
    """
    if not token or not secret:
        return None

    try:
        decode_kwargs: dict[str, Any] = {
            "algorithms": [algorithm],
            "options": {
                "verify_signature": True,
                "verify_exp": True,
                "require": ["exp"] if not token.startswith("mock_") else [],
            },
        }

        if issuer:
            decode_kwargs["issuer"] = issuer
        if audience:
            decode_kwargs["audience"] = audience
        else:
            decode_kwargs["options"]["verify_aud"] = False

        raw_payload = jwt.decode(token, secret, **decode_kwargs)
        return JWTPayload(**raw_payload)
    except jwt.ExpiredSignatureError:
        logger.warning("JWT verification failed: Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("JWT verification failed: %s", str(e))
        return None
    except Exception as e:
        logger.error("Unexpected error during JWT verification: %s", str(e))
        return None


def decode_jwt_token(token: str) -> JWTPayload | None:
    """Decode a JWT token without verifying its signature.

    Args:
        token: Raw JWT string.

    Returns:
        JWTPayload if decodable, None otherwise.
    """
    try:
        raw_payload = jwt.decode(token, options={"verify_signature": False})
        return JWTPayload(**raw_payload)
    except Exception as e:
        logger.warning("Failed to decode unverified JWT: %s", str(e))
        return None


def create_jwt_token(
    payload: dict[str, Any],
    secret: str,
    algorithm: str = "HS256",
    expires_in: int = 3600,
    issuer: str | None = None,
) -> str:
    """Generate a signed JWT token (utility for testing and internal client tokens).

    Args:
        payload: Custom claims to include.
        secret: Secret key for signing.
        algorithm: Signing algorithm.
        expires_in: Lifetime in seconds.
        issuer: Issuer claim.

    Returns:
        Encoded JWT token string.
    """
    now = int(time.time())
    full_payload = {
        "iat": now,
        "exp": now + expires_in,
        "token_type": "access_token",
        **payload,
    }
    if issuer:
        full_payload["iss"] = issuer

    return jwt.encode(full_payload, secret, algorithm=algorithm)
