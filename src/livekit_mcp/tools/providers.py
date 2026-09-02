"""Provider availability search tools for LiveKit Voice Agents."""

from datetime import UTC, date, datetime, time
import logging
from typing import Any
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from livekit_mcp.clients.db_client import DatabaseClient
from livekit_mcp.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Day mapping for RFC 5545 iCalendar codes and day names
WEEKDAY_MAP = {
    0: ("MO", "MONDAY"),
    1: ("TU", "TUESDAY"),
    2: ("WE", "WEDNESDAY"),
    3: ("TH", "THURSDAY"),
    4: ("FR", "FRIDAY"),
    5: ("SA", "SATURDAY"),
    6: ("SU", "SUNDAY"),
}


def is_date_matching_recurrence(target_date: date, recurrence_rule: str | None) -> bool:
    """Evaluate if a target date matches a provider's recurrence rule.

    Supports:
    - Empty / None (applies to all days in date range)
    - "DAILY" / "FREQ=DAILY"
    - iCalendar BYDAY rules: "BYDAY=MO,WE,FR" or "MO,TU,WE"
    - Full day names: "Monday, Wednesday, Friday"
    - Comma-separated day numbers: "0,1,2,3,4"
    """
    if not recurrence_rule or not recurrence_rule.strip():
        return True

    rrule_upper = recurrence_rule.strip().upper()

    if "DAILY" in rrule_upper:
        return True

    weekday_idx = target_date.weekday()
    day_code, day_name = WEEKDAY_MAP[weekday_idx]

    # Check 2-letter iCal code (e.g. "MO")
    if day_code in rrule_upper:
        return True

    # Check full day name (e.g. "MONDAY")
    if day_name in rrule_upper:
        return True

    # Check numeric day (e.g. "0" for Monday)
    if str(weekday_idx) in rrule_upper:
        return True

    return False


def convert_utc_time_to_tz(
    utc_time: time,
    target_date: date,
    target_tz_str: str,
) -> tuple[str, str]:
    """Convert UTC time to localized 12-hour formatted time string."""
    try:
        local_tz = ZoneInfo(target_tz_str)
    except Exception:
        local_tz = ZoneInfo("UTC")
        target_tz_str = "UTC"

    dt_utc = datetime.combine(target_date, utc_time, tzinfo=UTC)
    dt_local = dt_utc.astimezone(local_tz)

    formatted_time = dt_local.strftime("%I:%M %p").lstrip("0")
    tz_abbrev = dt_local.strftime("%Z") or target_tz_str

    return formatted_time, tz_abbrev


def format_slot_range(
    start_time: time,
    end_time: time,
    target_date: date,
    target_tz_str: str,
) -> tuple[str, str, str]:
    """Format start and end time range in target timezone."""
    start_str, tz_abbrev = convert_utc_time_to_tz(start_time, target_date, target_tz_str)
    end_str, _ = convert_utc_time_to_tz(end_time, target_date, target_tz_str)
    return start_str, end_str, tz_abbrev


def register_provider_tools(
    server: FastMCP,
    db_client: DatabaseClient | None = None,
    settings: Settings | None = None,
) -> None:
    """Register provider search tools with the MCP server."""
    app_settings = settings or get_settings()
    database = db_client or DatabaseClient(app_settings)

    @server.tool(
        name="search_provider_availability",
        description=(
            "Search available doctors and healthcare providers for an organization on a given date. "
            "Supports filtering by doctor name, specialization, or department. "
            "Automatically converts UTC database working hours to the organization's local timezone (e.g. IST)."
        ),
    )
    async def search_provider_availability(
        org_id: int | str,
        query_date: str,
        query: str | None = None,
        department: str | None = None,
        caller_phone: str | None = None,
    ) -> str:
        """Search provider availability in assist_db.

        Args:
            org_id: Organization ID (e.g. 66).
            query_date: Target date to search in 'YYYY-MM-DD' format (e.g. '2026-08-25').
            query: Optional search keyword to filter by doctor name.
            department: Optional medical department or specialization filter.
            caller_phone: Optional caller phone number for timezone detection.

        Returns:
            Formatted voice-ready string detailing available doctors and their time slots.
        """
        # Parse query date
        try:
            target_date = datetime.strptime(query_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            return f"Error: Invalid date format '{query_date}'. Please use YYYY-MM-DD (e.g. 2026-08-25)."

        logger.info(
            "Searching provider availability: org_id=%d, date=%s, query=%s, department=%s",
            org_id,
            query_date,
            query,
            department,
        )

        sql_query = """
            SELECT
                p.id AS provider_id,
                p.name AS provider_name,
                p.specialization,
                p.contact_phone,
                p.contact_email,
                p.status AS provider_status,
                pa.id AS availability_id,
                pa.org_id,
                pa.recurrence_rule,
                pa.start_time,
                pa.end_time,
                pa.start_date,
                pa.end_date,
                pa.capacity,
                pa.metadata,
                o.name AS organization_name,
                COALESCE(o.default_timezone, 'Asia/Kolkata') AS timezone
            FROM provider_availability pa
            INNER JOIN providers p ON p.id = pa.provider_id
            INNER JOIN provider_to_organization pto ON (pto.provider_id = p.id AND pto.org_id = pa.org_id)
            INNER JOIN organizations o ON o.id = pa.org_id
            WHERE pa.org_id = $1
              AND pto.is_active = TRUE
              AND (p.status = 'ACTIVE' OR p.status IS NULL)
              AND (pa.start_date IS NULL OR pa.start_date <= $2)
              AND (pa.end_date IS NULL OR pa.end_date >= $2)
              AND (
                  $3::text IS NULL
                  OR p.name ILIKE '%' || $3 || '%'
                  OR p.specialization ILIKE '%' || $3 || '%'
              )
              AND (
                  $4::text IS NULL
                  OR p.specialization ILIKE '%' || $4 || '%'
              )
            ORDER BY p.name ASC, pa.start_time ASC
        """

        try:
            filter_arg = query.strip() if query and query.strip() else None
            dept_arg = department.strip() if department and department.strip() else None
            rows = await database.fetch(sql_query, org_id, target_date, filter_arg, dept_arg)
        except Exception as e:
            logger.error("Failed to query provider_availability in assist_db: %s", str(e))
            return f"Error querying database: {e}"

        if not rows:
            formatted_date = target_date.strftime("%A, %b %d, %Y")
            filter_text = f" matching '{query}'" if query else (f" in {department}" if department else "")
            return f"No active provider schedules found for Organization {org_id} on {formatted_date}{filter_text}."

        # Filter rows by recurrence rule
        matching_slots: list[dict[str, Any]] = []
        org_name = rows[0]["organization_name"]
        org_tz = rows[0]["timezone"]

        for row in rows:
            rrule = row["recurrence_rule"]
            if is_date_matching_recurrence(target_date, rrule):
                matching_slots.append(dict(row))

        if not matching_slots:
            formatted_date = target_date.strftime("%A, %b %d, %Y")
            return f"No providers are scheduled to work on {formatted_date} (based on recurring schedule rules)."

        # Format output
        formatted_date = target_date.strftime("%A, %b %d, %Y")
        response_lines = [
            f" Available Providers for {org_name} on {formatted_date} (Timezone: {org_tz}):\n"
        ]

        # Group by provider
        providers_dict: dict[int, dict[str, Any]] = {}
        for slot in matching_slots:
            pid = slot["provider_id"]
            if pid not in providers_dict:
                providers_dict[pid] = {
                    "name": slot["provider_name"],
                    "specialization": slot["specialization"] or "General Practice",
                    "phone": slot["contact_phone"],
                    "slots": [],
                }

            start_t = slot["start_time"]
            end_t = slot["end_time"]
            start_str, end_str, tz_abbrev = format_slot_range(start_t, end_t, target_date, org_tz)
            cap = slot["capacity"]
            cap_str = f" (Max: {cap} patients)" if cap else ""
            providers_dict[pid]["slots"].append(f"{start_str} – {end_str} {tz_abbrev}{cap_str}")

        for _, pdata in providers_dict.items():
            slot_list = ", ".join(pdata["slots"])
            response_lines.append(
                f"• {pdata['name']} ({pdata['specialization']}): Available at {slot_list}."
            )

        return "\n".join(response_lines)
