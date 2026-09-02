#!/usr/bin/env python3
"""CLI utility to generate signed JWT access tokens for LiveKit MCP Server."""

import argparse
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from livekit_mcp.config import get_settings


def generate_token(
    user_id: str = "admin-user-id",
    client_id: str = "test-client-id",
    scope: str = "mcp:all",
    expires_in_hours: int = 24,
    secret: str | None = None,
) -> str:
    """Generate HS256 JWT access token compatible with mantra-auth and livekit-mcp."""
    settings = get_settings()
    jwt_secret = secret or settings.jwt_secret

    now = datetime.now(UTC)
    exp = now + timedelta(hours=expires_in_hours)

    payload = {
        "sub": user_id,
        "aud": client_id,
        "iss": settings.auth_server_url,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "scope": scope,
        "token_type": "access_token",
        "jti": uuid.uuid4().hex[:16],
    }

    token = jwt.encode(payload, jwt_secret, algorithm=settings.jwt_algorithm)
    return token


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate JWT token for LiveKit MCP")
    parser.add_argument("--user", default="admin-user-id", help="User ID (sub)")
    parser.add_argument("--client", default="test-client-id", help="Client ID (aud)")
    parser.add_argument("--scope", default="mcp:all", help="Token scopes")
    parser.add_argument("--hours", type=int, default=24, help="Token validity in hours")

    args = parser.parse_args()

    token = generate_token(
        user_id=args.user,
        client_id=args.client,
        scope=args.scope,
        expires_in_hours=args.hours,
    )

    print("\n🔑 Generated JWT Access Token:")
    print(token)
    print("\nDecoded Header/Payload info:")
    print(f"• User ID (sub): {args.user}")
    print(f"• Client ID (aud): {args.client}")
    print(f"• Valid for: {args.hours} hours")
    print(f"• Scope: {args.scope}\n")
