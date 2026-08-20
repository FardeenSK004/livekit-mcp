"""Unit tests for the greeting tool."""

import pytest

from livekit_mcp.server import create_mcp_server


@pytest.mark.asyncio
async def test_greeting_tool_registration():
    """Test that the greeting tool is properly registered with the MCP server."""
    server = create_mcp_server()
    tools = await server.list_tools()
    tool_names = [tool.name for tool in tools]
    assert "greet_user" in tool_names


@pytest.mark.asyncio
async def test_greeting_tool_execution():
    """Test calling the greeting tool."""
    server = create_mcp_server()
    result = await server.call_tool(
        name="greet_user",
        arguments={"name": "Alice", "message": "Testing LiveKit MCP"},
    )
    assert result is not None
    assert result.content is not None
    assert len(result.content) > 0

    # Extract text content from MCP result
    content_text = ""
    for item in result.content:
        if hasattr(item, "text"):
            content_text += item.text
        elif isinstance(item, str):
            content_text += item

    assert "Hello, Alice!" in content_text
    assert "Testing LiveKit MCP" in content_text
    assert "LiveKit MCP Server" in content_text
