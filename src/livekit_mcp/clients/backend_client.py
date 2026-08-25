"""HTTP Client to interact with MantraAssist-backend REST endpoints."""

import logging
from typing import Any

import httpx

from livekit_mcp.config import Settings, get_settings
from livekit_mcp.utils.timezone import to_utc_iso_string

logger = logging.getLogger(__name__)


class MantraAssistBackendClient:
    """Async HTTP client to query MantraAssist-backend for doctor schedules and availability."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.mantraassist_backend_url.rstrip("/")

    async def get_doctor_availability(
        self,
        org_id: int | str | None = None,
        date: str | None = None,
        doctor_name: str | None = None,
        department: str | None = None,
        caller_phone: str | None = None,
        caller_tz: str | None = None,
        timeout: float = 5.0,
    ) -> list[dict[str, Any]] | None:
        """Fetch calculated doctor availability from MantraAssist-backend endpoint.

        Guaranteed fixed schema sent in UTC every time:
            - org_id: Organization ID (or "" if missing)
            - date: Date string 'YYYY-MM-DD' in UTC (or "" if missing)
            - datetime: ISO 8601 UTC timestamp string 'YYYY-MM-DDTHH:MM:SS.000Z' (or "" if missing)
            - doc_name: Doctor name (or "" if missing)
            - department: Department / Specialization (or "" if missing)
            - caller_phone: Caller phone number (if available)

        Calls: GET /api/v1/providers/availability?org_id={org_id}&date={date}&datetime={datetime}&doc_name={doc_name}&department={department}
        Or: POST /api/v1/providers/availability

        Returns:
            List of provider objects with UTC time slots, or None if request fails.
        """
        url = f"{self.base_url}/api/v1/providers/availability"

        org_id_val = org_id if org_id is not None else ""
        doc_name_val = str(doctor_name).strip() if doctor_name and str(doctor_name).strip() else ""
        dept_val = str(department).strip() if department and str(department).strip() else ""

        # Always convert to UTC datetime format
        if date and str(date).strip():
            utc_datetime_val = to_utc_iso_string(str(date).strip(), source_tz_str=caller_tz or "UTC")
            utc_date_val = utc_datetime_val[:10]
        else:
            utc_datetime_val = ""
            utc_date_val = ""

        params: dict[str, Any] = {
            "org_id": org_id_val,
            "date": utc_date_val,
            "datetime": utc_datetime_val,
            "doc_name": doc_name_val,
            "department": dept_val,
        }
        if caller_phone:
            params["caller_phone"] = str(caller_phone).strip()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # 1. Try GET request
                logger.info("Querying MantraAssist backend GET %s with UTC params %s", url, params)
                resp = await client.get(url, params=params)

                if resp.status_code == 200:
                    data = resp.json()
                    return self._extract_providers(data)

                # 2. Try POST fallback if GET returns 404/405
                if resp.status_code in (404, 405):
                    logger.info("Retrying with POST %s", url)
                    post_resp = await client.post(url, json=params)
                    if post_resp.status_code == 200:
                        data = post_resp.json()
                        return self._extract_providers(data)

                logger.warning(
                    "MantraAssist backend returned HTTP %d: %s",
                    resp.status_code,
                    resp.text[:200],
                )
        except Exception as e:
            logger.error("Failed to connect to MantraAssist backend at %s: %s", url, e)

        return None

    def _extract_providers(self, data: Any) -> list[dict[str, Any]]:
        """Normalize response data to standard providers list."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "providers" in data and isinstance(data["providers"], list):
                return data["providers"]
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            if "data" in data and isinstance(data["data"], dict) and "providers" in data["data"]:
                return data["data"]["providers"]
            # Single provider dict fallback
            if "name" in data or "available_slots" in data:
                return [data]
        return []
