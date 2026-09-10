# Feature: Organization Processes Tool

## Purpose
The `fetch_org_processes` tool (alias `receive_org_processes`) fetches all processes and stage IDs with descriptions for an organization from `MantraAssist-backend`. Used during post-call analysis to assign the correct `process_id` and `new_stage_id`.

## Behavior
- `MantraAssistBackendClient.get_org_processes()` tries a fallback URL chain (`/v1/webhooks/mcp/processes` → `/v1/processes` → `/v1/webhooks/mcp`) with 5s timeout.
- 10-minute in-memory TTL cache per `org_id` (`_processes_cache`) avoids repeated overhead.
- Normalizes varied backend shapes (`processes`, `data`, single-object) into `{process_id, process_name, process_description, stage_ids, stages[{stage_id, stage_name, stage_description}]}`.
- Returns `[]` when all endpoints fail.

## Tool Signature
```python
async def fetch_org_processes(
    org_id: int | str,          # e.g. 77
) -> list[dict[str, Any]]       # Normalized processes + stages
# receive_org_processes: identical alias
```

## Source
- `src/livekit_mcp/tools/org_processes.py`
- Backend method: `src/livekit_mcp/clients/backend_client.py` → `get_org_processes()` / `_extract_processes()`
