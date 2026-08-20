# Feature: Greeting Tool

## Purpose
The `greet_user` tool is the initial test and verification tool for `livekit-mcp`. It validates that:
1. The MCP Server is listening and responding over SSE / JSON-RPC.
2. Authentication middleware has successfully verified the client.
3. Tool parameter schemas are correctly registered and parsed.

## Specification

### Signature
```python
async def greet_user(name: str, message: str = "Welcome to LiveKit MCP") -> str
```

### Parameters
- `name` (string, required): Name of the user or agent calling the tool.
- `message` (string, optional, default: `"Welcome to LiveKit MCP"`): Custom greeting text.

### Returns
Formatted string containing greeting, timestamp, and server environment status.
