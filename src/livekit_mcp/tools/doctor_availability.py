"""Doctor / Provider availability receiver tool supporting multiple providers and international timezones."""

from datetime import datetime
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from livekit_mcp.utils.timezone import convert_utc_slot_to_local, get_timezone_from_phone

logger = logging.getLogger(__name__)


def register_doctor_availability_tool(server: FastMCP) -> None:
    """Register doctor/provider availability receiver tool with the MCP server."""

    @server.tool(
        name="receive_doctor_availability",
        description=(
            "Receives calculated availability and open time slots in UTC for an array of doctors/providers "
            "from MantraAssist backend. Automatically detects the caller's timezone from their international "
            "phone number and converts all UTC slots into the caller's local time (e.g. EDT, GMT, IST, GST)."
        ),
    )
    async def receive_doctor_availability(
        user_id: int | None = None,
        org_id: int | None = None,
        name: str | None = None,
        date: str | None = None,
        available_slots: list[str] | None = None,
        providers: list[dict[str, Any]] | None = None,
        caller_phone: str | None = None,
        timezone: str | None = None,
    ) -> str:
        """Process and format availability for doctors/providers received from backend.

        Supports both single provider object format and list of provider objects.
        """
        # Normalize input to list of providers
        provider_list: list[dict[str, Any]] = []
        if providers and isinstance(providers, list):
            provider_list = providers
        elif name or available_slots is not None:
            provider_list = [
                {
                    "user_id": user_id,
                    "name": name or "Doctor",
                    "available_slots": available_slots or [],
                }
            ]

        # Extract org_id and date if passed in root or inside kwargs
        effective_org_id = org_id or kwargs.get("org_id") or 68
        target_date_str = str(date or kwargs.get("date") or datetime.now().strftime("%Y-%m-%d")).strip()

        # 1. Resolve target timezone
        if timezone and timezone.strip():
            target_tz = timezone.strip()
        elif caller_phone and caller_phone.strip():
            target_tz = get_timezone_from_phone(caller_phone, default_tz="Asia/Kolkata")
        else:
            target_tz = "Asia/Kolkata"

        # 2. Parse target date
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            formatted_date_str = target_date.strftime("%A, %b %d, %Y")
        except ValueError:
            formatted_date_str = target_date_str

        logger.info(
            "Processing availability: org_id=%s, date=%s, providers_count=%d, phone=%s, resolved_tz=%s",
            effective_org_id,
            target_date_str,
            len(provider_list),
            caller_phone,
            target_tz,
        )

        if not provider_list:
            return f"No doctor availability information found on {formatted_date_str}."

        lines = []

        # 3. Format each provider
        for i, provider in enumerate(provider_list, 1):
            doc_name = provider.get("name", "Doctor")
            raw_slots = provider.get("available_slots", [])

            if raw_slots:
                local_slots = []
                for slot in raw_slots:
                    slot_str = str(slot).strip()
                    # If already formatted with AM/PM (e.g. '10:00 AM – 11:00 AM'), keep as-is
                    if "AM" in slot_str.upper() or "PM" in slot_str.upper():
                        local_slots.append(slot_str)
                    else:
                        local_slots.append(
                            convert_utc_slot_to_local(
                                slot_str=slot_str,
                                target_date=target_date if 'target_date' in locals() else datetime.now().date(),
                                target_tz_str=target_tz,
                            )
                        )
                slots_text = ", ".join(local_slots)
                lines.append(f"{doc_name} is available on {formatted_date_str}: {slots_text}.")
            else:
                lines.append(f"{doc_name} has no open appointment slots on {formatted_date_str}.")

        return "\n".join(lines)
