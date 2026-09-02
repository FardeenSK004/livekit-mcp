"""Organization Processes & Stages tool for CRM stage and process assignment."""

import json
import logging
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from livekit_mcp.clients.backend_client import MantraAssistBackendClient
from livekit_mcp.config import Settings, get_settings

logger = logging.getLogger(__name__)


def register_org_processes_tool(
    server: FastMCP,
    settings: Settings | None = None,
    backend_client: MantraAssistBackendClient | None = None,
) -> None:
    """Register organization processes and stages tool with the MCP server."""
    app_settings = settings or get_settings()
    ma_client = backend_client or MantraAssistBackendClient(app_settings)

    @server.tool(
        name="fetch_org_processes",
        description=(
            "Fetch all processes and stage IDs along with their descriptions mapped to an organization. "
            "Used during post-call analysis to assign the correct process_id and new_stage_id."
        ),
    )
    async def fetch_org_processes(
        org_id: Annotated[int | str, "The organization ID to look up processes and stages for (e.g. 77)"],
    ) -> list[dict[str, Any]]:
        """Fetch processes and stages for the specified organization."""
        logger.info("[MCP-TOOL] fetch_org_processes called with org_id=%s", org_id)
        processes = await ma_client.get_org_processes(org_id=org_id)
        logger.info("[MCP-TOOL] fetch_org_processes returning %d processes: %s", len(processes), json.dumps(processes, default=str))
        return processes

    @server.tool(
        name="receive_org_processes",
        description=(
            "Alias for fetch_org_processes. Fetch all processes and stage IDs with descriptions for an organization."
        ),
    )
    async def receive_org_processes(
        org_id: Annotated[int | str, "The organization ID to look up processes and stages for (e.g. 77)"],
    ) -> list[dict[str, Any]]:
        """Alias for fetch_org_processes."""
        return await fetch_org_processes(org_id=org_id)
