# API & Protocol Endpoints

## Endpoints

### 1. `GET /health`
- **Auth:** None (Public)
- **Description:** Health and readiness check endpoint.
- **Response:**
  ```json
  {
    "status": "healthy",
    "version": "0.1.0",
    "auth_enabled": true,
    "lkt_api_configured": true
  }
  ```

### 2. `GET /sse`
- **Auth:** Bearer token in header or `?token=<jwt>`
- **Description:** Opens Server-Sent Events stream for MCP client communication. Returns the `/messages` URI for subsequent RPC requests.

### 3. `POST /messages`
- **Auth:** Bearer token in header or `?token=<jwt>`
- **Description:** JSON-RPC 2.0 endpoint for MCP commands (tool listing, tool execution, prompts, resources).

---

## Registered MCP Tools

### `greet_user`
- **Description:** Formats a welcome message and returns system status for the caller.
- **Arguments:**
  - `name` (string, required): The name of the user or agent.
  - `message` (string, optional): An optional custom greeting message.
- **Returns:** String formatted greeting with timestamp and caller context.
