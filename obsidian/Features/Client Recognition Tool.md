# Feature: Client Recognition Tool

## Purpose
The `recognize_client` tool identifies an inbound caller by organization and phone number **before the greeting**, so the LiveKit Voice Agent can personalize the call. Unknown, timed-out, or failed lookups resolve to an anonymous caller — the call is never blocked.

## Flow
1. Normalize the caller number via `normalize_phone_number()` (E.164 style; bare 10-digit numbers assumed Indian `+91`).
2. `MantraAssistBackendClient.recognize_client()` POSTs `{org_id, phone_number}` to `POST /api/v1/webhooks/client-recognition` (3s timeout, `ngrok-skip-browser-warning` header).
3. Unwrap `{"client_name"}` (tolerates `{data: {client_name}}` envelope); non-200 / exception → `None`.
4. Tool returns `{"client_name": "<name>" | null}` as a JSON string.

## Tool Signature
```python
async def recognize_client(
    org_id: int | str,      # Organization ID for the inbound number
    phone_number: str,      # Inbound caller number, preferably E.164
) -> str                    # JSON: {"client_name": str | null}
```

## Source
- `src/livekit_mcp/tools/client_recognition.py`
- Backend method: `src/livekit_mcp/clients/backend_client.py` → `recognize_client()`
- Registered in `server.py` (`create_mcp_server`); **not** re-exported from `tools/__init__.py` (gap noted 2026-09-08).
