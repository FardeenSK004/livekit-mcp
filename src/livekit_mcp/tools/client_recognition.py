"""Client recognition tool for inbound caller context."""

import json
import logging
import re
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from livekit_mcp.clients.backend_client import MantraAssistBackendClient
from livekit_mcp.config import Settings, get_settings

logger = logging.getLogger(__name__)


def normalize_phone_number(phone_number: str) -> str:
    """Normalize the caller number to the E.164-style format used by MA."""
    value = str(phone_number or "").strip()
    if value.startswith("+"):
        return "+" + re.sub(r"\D", "", value)

    digits = re.sub(r"\D", "", value)
    if len(digits) == 10:
        return f"+91{digits}"
    return f"+{digits}" if digits else ""


def register_client_recognition_tool(
    server: FastMCP,
    settings: Settings | None = None,
    backend_client: MantraAssistBackendClient | None = None,
) -> None:
    """Register the inbound client recognition tool."""
    app_settings = settings or get_settings()
    ma_client = backend_client or MantraAssistBackendClient(app_settings)

    @server.tool(
        name="recognize_client",
        description=(
            "Identify an inbound caller by organization and phone number before the greeting. "
            "Returns the client name, recent AI summaries, and custom fields when registered. "
            "Returns null client_name and empty metadata when no client is found."
        ),
    )
    async def recognize_client(
        org_id: Annotated[int | str, "Organization ID associated with the inbound phone number"],
        phone_number: Annotated[str, "Inbound caller phone number, preferably in E.164 format"],
    ) -> str:
        """Return the registered client identity and metadata for anonymous-call context."""
        normalized_phone = normalize_phone_number(phone_number)
        logger.info(
            "[MCP-TOOL] recognize_client called for org_id=%s, phone=%s",
            org_id,
            normalized_phone,
        )
        result = await ma_client.recognize_client(
            org_id=org_id,
            phone_number=normalized_phone,
        )
        response_data = result if isinstance(result, dict) else {}
        if isinstance(response_data.get("data"), dict):
            response_data = response_data["data"]
        elif isinstance(response_data.get("result"), dict):
            response_data = response_data["result"]

        client_name = None
        client_metadata = {
            "ai_summaries": [],
            "custom_fields": [],
        }
        if isinstance(response_data, dict):
            client_name = (
                response_data.get("client_name")
                or response_data.get("name")
                or response_data.get("full_name")
            )
            raw_metadata = response_data.get("client_metadata")
            if isinstance(raw_metadata, dict):
                if isinstance(raw_metadata.get("ai_summaries"), list):
                    client_metadata["ai_summaries"] = raw_metadata["ai_summaries"]
                if isinstance(raw_metadata.get("custom_fields"), list):
                    client_metadata["custom_fields"] = raw_metadata["custom_fields"]

        return json.dumps({
            "client_name": client_name,
            "client_metadata": client_metadata,
        })
