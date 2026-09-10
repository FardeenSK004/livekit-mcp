# Feature: Department Discovery Tool

## Purpose
The `get_org_departments` tool fetches the medical departments/specialties supported by an organization from `MantraAssist-backend`. Used during live calls when a caller gives a broad symptom (e.g. an eye problem) and the voice agent needs one clarifying question before checking doctor availability.

## Behavior
- `MantraAssistBackendClient.get_org_departments()` calls `GET /v1/webhooks/mcp/departments?org_id={org_id}` with 5s timeout and `ngrok-skip-browser-warning` header.
- 10-minute in-memory TTL cache per `org_id` (`_departments_cache`) avoids repeated overhead; only non-empty payloads are cached.
- `_normalize_department_payload()` tolerates varied backend shapes (`departments`, `specializations`, `data`, `results`, dict-of-lists, list of `{name|department|specialization}` objects) and returns deduplicated, casefold-sorted names.
- Returns `{"org_id": <id>, "departments": []}` when the backend fails or yields nothing — never blocks the call.

## Tool Signature
```python
async def get_org_departments(
    org_id: int | str,          # The organization ID for the current call
) -> dict[str, Any]             # {"org_id": <id>, "departments": [<names>]}
```

## Source
- `src/livekit_mcp/tools/department_list.py`
- Backend method: `src/livekit_mcp/clients/backend_client.py` → `get_org_departments()` / `_normalize_department_payload()`
- Registered in `server.py` (`create_mcp_server`); **not** re-exported from `tools/__init__.py` (gap noted 2026-09-10).
