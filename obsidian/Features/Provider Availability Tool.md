# Feature: Provider Availability Search Tool

## Purpose
The `search_provider_availability` tool enables the LiveKit Voice Agent to dynamically look up doctor/provider availability in `assist_db` during live telephony calls.

## Database Tables Queried
- **`provider_availability`**: `provider_id`, `org_id`, `recurrence_rule`, `start_time` (UTC), `end_time` (UTC), `start_date`, `end_date`, `capacity`
- **`providers`**: `id`, `name`, `specialization`, `contact_phone`, `status`
- **`provider_to_organization`**: `provider_id`, `org_id`, `is_active`
- **`organizations`**: `id`, `name`, `default_timezone`

## Timezone Translation
Times stored in `provider_availability.start_time` and `end_time` are in **UTC**. The tool uses Python `zoneinfo.ZoneInfo` combined with `Organizations.default_timezone` (default `Asia/Kolkata`) to convert UTC working hours into localized readable times (e.g. `10:00 AM – 02:00 PM IST`).

## Recurrence Evaluation
Evaluates `recurrence_rule` strings against the target date:
- RFC 5545 day codes (`MO`, `TU`, `WE`, `TH`, `FR`, `SA`, `SU`)
- English day names (`Monday`, `Tuesday`, etc.)
- Daily / Empty patterns

## Tool Signature
```python
async def search_provider_availability(
    org_id: int,
    query_date: str,  # Format: "YYYY-MM-DD"
    query: str | None = None,  # Filter by name or specialization
) -> str
```
