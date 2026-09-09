"""Async HTTP client for interacting with the LKT voice agent engine."""

import logging
from typing import Any

import httpx

from livekit_mcp.config import Settings

logger = logging.getLogger(__name__)


class LktClient:
    """Client for LKT FastAPI service (:8081)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.base_url = settings.lkt_api_base_url.rstrip("/")
        self.timeout = settings.lkt_api_timeout
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def health_check(self) -> dict[str, Any]:
        """Check health status of the LKT service."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
                response = await client.get("/health")
                if response.status_code == 200:
                    return response.json()
                return {
                    "healthy": False,
                    "status_code": response.status_code,
                    "error": response.text,
                }
        except Exception as e:
            logger.warning("LKT health check failed: %s", str(e))
            return {"healthy": False, "error": str(e)}

    async def get_active_calls(self, token: str | None = None) -> dict[str, Any]:
        """Fetch active calls from LKT."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                response = await client.get("/v1/dashboard/active-calls", headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to fetch active calls from LKT: %s", str(e))
            return {"error": str(e)}

    async def trigger_outbound_call(
        self, payload: dict[str, Any], token: str | None = None
    ) -> dict[str, Any]:
        """Trigger an outbound telephony call via LKT."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                response = await client.post(
                    "/api/v1/webhooks/telephony", json=payload, headers=headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to trigger outbound call via LKT: %s", str(e))
            return {"error": str(e)}
