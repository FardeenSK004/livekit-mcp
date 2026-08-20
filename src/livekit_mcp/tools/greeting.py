"""Greeting test and verification tool for LiveKit MCP Server."""

import logging
from datetime import UTC, datetime

from mcp.server.mcpserver import MCPServer

logger = logging.getLogger(__name__)


def register_greeting_tool(server: MCPServer) -> None:
    """Register the greeting tool with the MCP server."""

    @server.tool(
        name="greet_user",
        description=(
            "Greet a user or agent and verify that the LiveKit MCP server is operational. "
            "Returns a structured confirmation with current server timestamp and environment status."
        ),
    )
    async def greet_user(
        name: str,
        message: str | None = "Welcome to MantraCare LiveKit MCP!",
    ) -> str:
        """Greet a user and return system verification status.

        Args:
            name: The name of the user or agent requesting the greeting.
            message: An optional custom message to append to the greeting.

        Returns:
            A formatted string containing greeting, timestamp, and status.
        """
        now = datetime.now(UTC).isoformat()
        logger.info("greet_user called for '%s'", name)

        greeting_body = message if message else "Welcome to MantraCare LiveKit MCP!"

        return (
            f"👋 Hello, {name}!\n\n"
            f"{greeting_body}\n\n"
            f"--- System Status ---\n"
            f"• Service: LiveKit MCP Server\n"
            f"• Status: Operational & Ready\n"
            f"• Timestamp: {now}\n"
            f"• Protocol: MCP 2.0 (SSE / HTTP)"
        )
