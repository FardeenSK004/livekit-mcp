"""Authentication module for LiveKit MCP Server."""

from livekit_mcp.auth.hmac import build_signature, build_signed_headers, canonicalize_payload, verify_signature
from livekit_mcp.auth.jwt import JWTPayload, decode_jwt_token, verify_jwt_token
from livekit_mcp.auth.middleware import AuthMiddleware

__all__ = ["JWTPayload", "verify_jwt_token", "decode_jwt_token", "AuthMiddleware", "build_signature", "build_signed_headers", "canonicalize_payload", "verify_signature"]
