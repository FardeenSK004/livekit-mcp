"""Async HTTP client for interacting with the Mantra Auth OAuth 2.1 server."""

import logging
from typing import Any

import httpx

from livekit_mcp.config import Settings

logger = logging.getLogger(__name__)


class AuthClient:
    """Client for Mantra Auth OAuth2.1 server (:3000)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.base_url = settings.auth_server_url.rstrip("/")
        self._client = client

    async def introspect_token(self, token: str) -> dict[str, Any]:
        """Introspect an access token against mantra-auth."""
        url = f"{self.base_url}/api/oauth/introspect"
        data = {"token": token, "token_type_hint": "access_token"}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning(
                    "Token introspection returned %d: %s", response.status_code, response.text
                )
                return {"active": False, "error": response.text}
        except Exception as e:
            logger.error("Token introspection request failed: %s", str(e))
            return {"active": False, "error": str(e)}

    async def get_user_info(self, token: str) -> dict[str, Any]:
        """Fetch userinfo from mantra-auth."""
        url = f"{self.base_url}/api/oauth/userinfo"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            logger.error("Userinfo request failed: %s", str(e))
            return {"error": str(e)}
