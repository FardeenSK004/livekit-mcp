"""Medical department discovery tool for symptom clarification during calls."""

import logging
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from livekit_mcp.clients.backend_client import MantraAssistBackendClient
from livekit_mcp.config import Settings, get_settings

logger = logging.getLogger(__name__)


def register_department_tool(
    server: FastMCP,
    settings: Settings | None = None,
    backend_client: MantraAssistBackendClient | None = None,
) -> None:
    """Register organization-specific department discovery."""
    app_settings = settings or get_settings()
    ma_client = backend_client or MantraAssistBackendClient(app_settings)

    @server.tool(
        name="get_org_departments",
        description=(
            "Fetch the medical departments or specialties supported by an organization. "
            "Use this when a caller gives a broad symptom such as an eye problem and "
            "you need one clarifying question before checking doctor availability."
        ),
    )
    async def get_org_departments(
        org_id: Annotated[int | str, "The organization ID for the current call"],
    ) -> dict[str, Any]:
        logger.info("[MCP-TOOL] get_org_departments called with org_id=%s", org_id)
        return await ma_client.get_org_departments(org_id)
