"""Timezone resolution and conversion utilities based on phone numbers and IANA timezones."""

from datetime import UTC, date, datetime, time, timedelta
import logging
import re
from zoneinfo import ZoneInfo

import phonenumbers
from phonenumbers import timezone as phone_tz

logger = logging.getLogger(__name__)

# Normalize legacy timezones (e.g. Asia/Calcutta -> Asia/Kolkata)
TZ_ALIASES = {
    "Asia/Calcutta": "Asia/Kolkata",
}


def get_timezone_from_phone(phone_number: str | None, default_tz: str = "UTC") -> str:
    """Resolve IANA timezone string from an international phone number.

    Examples:
        - '+12025550123'  -> 'America/New_York' (or 'America/Chicago', etc.)
        - '+442071838750' -> 'Europe/London'
        - '+918360625862' -> 'Asia/Kolkata'
        - '+971501234567' -> 'Asia/Dubai'
        - '+61298765432'  -> 'Australia/Sydney'
    """
    if not phone_number or not str(phone_number).strip():
        return default_tz

    cleaned = str(phone_number).strip().replace(" ", "").replace("-", "")
    if len(cleaned) == 10 and not cleaned.startswith("+"):
        cleaned = "+91" + cleaned
    elif not cleaned.startswith("+"):
        cleaned = "+" + cleaned

    try:
        parsed = phonenumbers.parse(cleaned, None)
        if not phonenumbers.is_valid_number(parsed):
            logger.info("Phone %s parsed as national/local format, defaulting to %s", phone_number, default_tz)
            return default_tz

        tz_list = phone_tz.time_zones_for_number(parsed)
        if tz_list and len(tz_list) > 0 and tz_list[0] != "Etc/Unknown":
            resolved = tz_list[0]
            return TZ_ALIASES.get(resolved, resolved)
    except Exception as e:
        logger.warning("Error resolving timezone for phone %s: %s", phone_number, e)

    return default_tz


def parse_time_str(time_str: str) -> time | None:
    """Parse time strings like '04:30', '4:30', '04:30:00', '4:30 PM'."""
    cleaned = time_str.strip().upper()

    # Match 12-hour format: '4:30 PM', '04:30 PM', '4 PM'
    match_12h = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$", cleaned)
    if match_12h:
        hour = int(match_12h.group(1))
        minute = int(match_12h.group(2) or 0)
        meridiem = match_12h.group(3)
        if meridiem == "PM" and hour < 12:
            hour += 12
        elif meridiem == "AM" and hour == 12:
            hour = 0
        return time(hour, minute)

    # Match 24-hour format: '04:30', '14:30', '04:30:00'
    match_24h = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", cleaned)
    if match_24h:
        return time(int(match_24h.group(1)), int(match_24h.group(2)))

    return None


def resolve_date_string(date_str: str | None, source_tz_str: str = "Asia/Kolkata") -> date:
    """Resolve strings like 'today', 'tomorrow', 'yesterday', '2026-08-25' into a date object."""
    try:
        source_tz = ZoneInfo(source_tz_str)
    except Exception:
        source_tz = ZoneInfo("UTC")

    now_local = datetime.now(source_tz).date()

    if not date_str or not str(date_str).strip():
        return now_local

    cleaned = str(date_str).strip().lower()

    if cleaned in ("today", "now"):
        return now_local
    if cleaned == "tomorrow":
        return now_local + timedelta(days=1)
    if cleaned == "yesterday":
        return now_local - timedelta(days=1)

    # Try ISO or YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(cleaned[:10], fmt).date()
        except ValueError:
            pass

    return now_local


def to_utc_iso_string(
    date_str: str,
    time_str: str | None = None,
    source_tz_str: str = "UTC",
) -> str:
    """Convert a local date (and optional time) string into an ISO 8601 UTC timestamp string.

    Examples:
        - to_utc_iso_string('today', source_tz_str='Asia/Kolkata') -> '2026-08-25T00:00:00.000Z'
        - to_utc_iso_string('2026-08-25', '10:00', source_tz_str='America/New_York') -> '2026-08-25T14:00:00.000Z'
    """
    try:
        source_tz = ZoneInfo(source_tz_str)
    except Exception:
        source_tz = ZoneInfo("UTC")

    try:
        # If date_str is already ISO format (e.g. contains 'T' and 'Z')
        if date_str and "T" in str(date_str):
            dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        # Resolve date
        d = resolve_date_string(date_str, source_tz_str)
        t = parse_time_str(time_str) if time_str else time(0, 0, 0)
        if not t:
            t = time(0, 0, 0)

        dt_local = datetime.combine(d, t, tzinfo=source_tz)
        dt_utc = dt_local.astimezone(UTC)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception:
        return datetime.now(UTC).strftime("%Y-%m-%dT00:00:00.000Z")


def convert_utc_slot_to_local(
    slot_str: str,
    target_date: date,
    target_tz_str: str = "Asia/Kolkata",
) -> str:
    """Convert a UTC time slot string into a readable 12-hour string in the caller's timezone.

    Accepts formats:
        - "04:30 - 05:30" (UTC 24h range)
        - "04:30 – 05:30" (UTC range with en-dash)
        - "04:30" (Single UTC start time)
        - "2026-08-25T04:30:00Z" (ISO UTC timestamp)
        - "10:00 AM – 11:00 AM" (Already formatted string)
    """
    cleaned = slot_str.strip()

    try:
        local_tz = ZoneInfo(target_tz_str)
    except Exception:
        local_tz = ZoneInfo("UTC")
        target_tz_str = "UTC"

    # 1. Check if it's an ISO 8601 string
    if "T" in cleaned:
        try:
            iso_dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
            if iso_dt.tzinfo is None:
                iso_dt = iso_dt.replace(tzinfo=UTC)
            local_dt = iso_dt.astimezone(local_tz)
            time_str = local_dt.strftime("%I:%M %p").lstrip("0")
            tz_code = local_dt.strftime("%Z") or target_tz_str
            return f"{time_str} {tz_code}"
        except Exception:
            pass

    # 2. Check for range separators: " - ", " – ", " to "
    range_match = re.split(r"\s*(?:–|-|\bto\b)\s*", cleaned, maxsplit=1)
    if len(range_match) == 2:
        start_t = parse_time_str(range_match[0])
        end_t = parse_time_str(range_match[1])

        if start_t and end_t:
            # Combine with target date as UTC
            start_dt_utc = datetime.combine(target_date, start_t, tzinfo=UTC)
            end_dt_utc = datetime.combine(target_date, end_t, tzinfo=UTC)

            start_dt_local = start_dt_utc.astimezone(local_tz)
            end_dt_local = end_dt_utc.astimezone(local_tz)

            start_str = start_dt_local.strftime("%I:%M %p").lstrip("0")
            end_str = end_dt_local.strftime("%I:%M %p").lstrip("0")
            tz_code = start_dt_local.strftime("%Z") or target_tz_str

            return f"{start_str} – {end_str} {tz_code}"

    # 3. Single time format: "04:30"
    single_t = parse_time_str(cleaned)
    if single_t:
        single_dt_utc = datetime.combine(target_date, single_t, tzinfo=UTC)
        single_dt_local = single_dt_utc.astimezone(local_tz)
        time_str = single_dt_local.strftime("%I:%M %p").lstrip("0")
        tz_code = single_dt_local.strftime("%Z") or target_tz_str
        return f"{time_str} {tz_code}"

    # 4. Fallback if already text formatted
    return f"{cleaned} ({target_tz_str})"
