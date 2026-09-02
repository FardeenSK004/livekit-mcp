"""Database logging utilities for MCP Server."""

import json
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

from livekit_mcp.clients.db_client import DatabaseClient
from livekit_mcp.config import get_settings

logger = logging.getLogger(__name__)

# In-memory circular buffer of recent events for instant dashboard telemetry
_recent_events: deque[dict[str, Any]] = deque(maxlen=100)


def get_recent_events(limit: int = 25) -> list[dict[str, Any]]:
    """Retrieve the most recent MCP events from the in-memory buffer."""
    return list(_recent_events)[:limit]


async def save_mcp_event(
    event_type: str,
    event_source: str,
    event_payload: dict[str, Any],
    event_status: str = "success",
    event_error: str = "",
    event_log: str = "",
    call_id: str = "",
) -> None:
    """Save a single event to in-memory buffer and optional mcp_events audit table."""
    now_iso = datetime.now(UTC).isoformat()
    _recent_events.appendleft({
        "call_id": str(call_id or ""),
        "event_type": event_type,
        "event_source": event_source,
        "event_payload": event_payload,
        "event_status": event_status,
        "event_error": event_error or "",
        "created_at": now_iso,
    })

    settings = get_settings()
    db_client = DatabaseClient(settings, db_url=settings.mcp_events_db_url)

    try:
        pool = await db_client.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mcp_events (
                    id SERIAL PRIMARY KEY,
                    call_id VARCHAR(255),
                    event_type VARCHAR(255),
                    event_source VARCHAR(255),
                    event_payload JSONB,
                    event_log TEXT,
                    event_status VARCHAR(50),
                    event_error TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            await conn.execute(
                """
                INSERT INTO mcp_events (call_id, event_type, event_source, event_payload, event_log, event_status, event_error)
                VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7)
                """,
                str(call_id),
                event_type,
                event_source,
                json.dumps(event_payload, default=str),
                str(event_log or "")[:8000],
                event_status,
                event_error or "",
            )
    except Exception as e:
        logger.debug(f"DB event save skipped: {e}")

