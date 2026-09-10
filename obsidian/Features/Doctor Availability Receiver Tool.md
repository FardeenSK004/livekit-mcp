# Feature: Doctor Availability Receiver Tool

## Purpose
The `receive_doctor_availability` tool resolves doctor working hours and open consultation slots for an organization and formats them into voice-agent-ready local-time strings. It accepts pre-supplied provider/slot arrays **or** queries `MantraAssist-backend` live, with a direct `assist_db` fallback when the backend is unreachable.

## Signature (current)
```python
async def receive_doctor_availability(
    user_id: int | str | None = None,
    org_id: int | str | None = None,
    name: str | None = None,                    # doctor name filter (also builds single-provider list with available_slots)
    date: str | None = None,                    # YYYY-MM-DD, 'today', 'tomorrow', ... (default: today)
    department: str | None = None,              # department / specialization filter
    available_slots: list[str] | None = None,   # pre-supplied UTC slots for `name`
    providers: list[dict[str, Any]] | None = None,  # pre-supplied provider array
    caller_phone: str | None = None,            # caller number for timezone auto-detection
    timezone: str | None = None,                # explicit tz override (wins over phone detection)
) -> str
```

## Flow
1. Resolve target timezone: explicit `timezone` → `phonenumbers` detection from `caller_phone` → default `Asia/Kolkata`.
2. Resolve the target date via `resolve_date_string()` (handles relative dates).
3. Resolve providers: (A) pre-supplied `providers` / `name`+`available_slots`; else (B) `MantraAssistBackendClient.get_doctor_availability()` (`GET /v1/webhooks/mcp`, `POST` fallback, fixed UTC schema `{org_id, date, datetime, doc_name, department, caller_phone}`); else (C) direct `assist_db` query (`provider_availability` ⨝ `providers`).
4. Localize each UTC slot with `convert_utc_slot_to_local()` (slots already containing AM/PM pass through untouched) and emit `"<Name> (User ID: <id>) is available on <date>: <slots>."` lines, including `user_id` injection for post-call appointment resolution.

## Backend Contract
`GET /v1/webhooks/mcp` (fallback `POST`) with UTC params `org_id`, `date` (`YYYY-MM-DD`), `datetime` (ISO-8601 UTC), `doc_name`, `department`, `caller_phone`. See `backend_client.get_doctor_availability()` / `_extract_providers()` for normalization.

## Source
- `src/livekit_mcp/tools/doctor_availability.py`
- Backend method: `src/livekit_mcp/clients/backend_client.py` → `get_doctor_availability()`
- Timezone: `src/livekit_mcp/utils/timezone.py` (`get_timezone_from_phone`, `resolve_date_string`, `convert_utc_slot_to_local`)
