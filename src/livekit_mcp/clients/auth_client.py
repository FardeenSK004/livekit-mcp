"""Mantra Auth OAuth Introspection Client."""

import logging
from typing import Any, Dict, Optional

import httpx

from livekit_mcp.auth.jwt import JWTPayload
from livekit_mcp.config import Settings, get_settings

logger = logging.getLogger(__name__)


class AuthClient:
    """Async client for Mantra Auth OAuth 2.1 token introspection."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.auth_server_url = self.settings.auth_server_url.rstrip("/")

    async def introspect_token(self, token: str) -> Optional[JWTPayload]:
        """Introspect access token via Mantra Auth POST /api/oauth/introspect.

        Args:
            token: Raw access token or bearer token string.

        Returns:
            JWTPayload if active, None if inactive or verification failed.
        """
        introspect_url = f"{self.auth_server_url}/api/oauth/introspect"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "token": token,
            "token_type_hint": "access_token",
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(introspect_url, data=payload, headers=headers)
                if response.status_code == 200:
                    data: Dict[str, Any] = response.json()
                    if data.get("active") is True:
                        logger.info("OAuth introspection succeeded for sub=%s", data.get("sub"))
                        return JWTPayload(
                            sub=str(data.get("sub", data.get("username", "agent"))),
                            aud=data.get("client_id"),
                            iss=self.auth_server_url,
                            scope=data.get("scope", "mcp:all"),
                            token_type=data.get("token_type", "access_token"),
                        )
                    else:
                        logger.warning("OAuth introspection rejected token: active=false")
                        return None
                else:
                    logger.warning(
                        "OAuth introspection failed with HTTP %d: %s",
                        response.status_code,
                        response.text[:200],
                    )
                    return None
        except Exception as e:
            logger.error("Error connecting to Mantra Auth introspection endpoint: %s", e)
            return None
