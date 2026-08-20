# Data Flow

## 1. Client Connection & Authentication Flow

```
Client                 LiveKit MCP Server               Mantra Auth
  │                            │                             │
  ├─ GET /sse?token=<jwt> ────>│                             │
  │  (or Bearer Header)        ├─ Verify HS256 JWT           │
  │                            │  (or call /introspect) ────>│
  │                            │<── Token Valid ─────────────┤
  │<── 200 SSE Stream ─────────┤
  │    (endpoint: /messages)   │
```

## 2. Tool Execution Flow

```
Client                 LiveKit MCP Server                 LKT Engine
  │                            │                             │
  ├─ POST /messages?session_id │                             │
  │  {"method": "tools/call",  │                             │
  │   "params": {"name": ...}} │                             │
  │                           ─┼─ Authenticate request       │
  │                            ├─ Execute tool handler       │
  │                            │  (calls LktClient if needed)─>│
  │                            │<── Response from LKT ───────┤
  │<── 200 JSON-RPC Result ────┤
```
