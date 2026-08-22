"""Doctor / Provider availability receiver tool supporting multiple providers and international timezones."""

from datetime import datetime
import logging
from typing import Any

from mcp.server.mcpserver import MCPServer

from livekit_mcp.utils.timezone import convert_utc_slot_to_local, get_timezone_from_phone

logger = logging.getLogger(__name__)


def register_doctor_availability_tool(server: MCPServer) -> None:
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
        org_id: int,
        date: str,
        providers: list[dict[str, Any]],
        caller_phone: str | None = None,
        timezone: str | None = None,
    ) -> str:
        """Process and format availability for an array of doctors received from backend.

        Args:
            org_id: Organization ID.
            date: Target date in 'YYYY-MM-DD' format.
            providers: Array of provider objects, each containing:
                - user_id (int): Doctor ID from users table.
                - name (str): Doctor's full name (e.g. 'Dr. Ananya Sharma').
                - available_slots (list[str]): List of open UTC time slots (e.g. ['04:30 - 05:30']).
            caller_phone: Optional international phone number of the caller (e.g. '+12025550123').
            timezone: Optional explicit IANA timezone string (overrides phone detection if provided).

        Returns:
            Clean voice-ready text with all doctors and their time slots converted to the caller's timezone.
        """
        # 1. Resolve target timezone: explicit timezone > phone number timezone > default (Asia/Kolkata)
        if timezone and timezone.strip():
            target_tz = timezone.strip()
        elif caller_phone and caller_phone.strip():
            target_tz = get_timezone_from_phone(caller_phone, default_tz="Asia/Kolkata")
        else:
            target_tz = "Asia/Kolkata"

        # 2. Parse target date
        try:
            target_date = datetime.strptime(date.strip(), "%Y-%m-%d").date()
            formatted_date_str = target_date.strftime("%A, %b %d, %Y")
        except ValueError:
            target_date = datetime.now().date()
            formatted_date_str = date.strip()

        logger.info(
            "Processing availability: org_id=%d, date=%s, providers_count=%d, phone=%s, resolved_tz=%s",
            org_id,
            date,
            len(providers),
            caller_phone,
            target_tz,
        )

        if not providers:
            return f"No doctors or providers are available for Organization {org_id} on {formatted_date_str}."

        lines = [
            f"📅 **Available Doctors on {formatted_date_str}** (Local Timezone: {target_tz}):\n",
        ]

        # 3. Format each provider and convert their UTC slots to local time
        for i, provider in enumerate(providers, 1):
            name = provider.get("name", "Doctor")
            user_id = provider.get("user_id", "N/A")
            raw_slots = provider.get("available_slots", [])

            if raw_slots:
                local_slots = [
                    convert_utc_slot_to_local(
                        slot_str=slot,
                        target_date=target_date,
                        target_tz_str=target_tz,
                    )
                    for slot in raw_slots
                ]
                slots_text = ", ".join(local_slots)
            else:
                slots_text = "No open slots"

            lines.append(f"{i}. **{name}** (User ID: {user_id})\n   • Available Slots: {slots_text}\n")

        caller_info = f" | Caller Phone: {caller_phone}" if caller_phone else ""
        lines.append(f"**Org ID:** {org_id}{caller_info}")

        return "\n".join(lines)
