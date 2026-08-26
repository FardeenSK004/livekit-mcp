"""Database logging utilities for MCP Server."""

import json
import logging
from typing import Any

from livekit_mcp.clients.db_client import DatabaseClient
from livekit_mcp.config import get_settings

logger = logging.getLogger(__name__)


async def save_mcp_event(
    event_type: str,
    event_source: str,
    event_payload: dict[str, Any],
    event_status: str = "success",
    event_error: str = "",
    event_log: str = "",
    call_id: str = "",
) -> None:
    """Save a single event to the mcp_events audit table."""
    settings = get_settings()
    # Use dedicated MCP events database if configured, otherwise fallback to default
    db_client = DatabaseClient(settings, db_url=settings.mcp_events_db_url)
    
    try:
        pool = await db_client.get_pool()
        async with pool.acquire() as conn:
            # Auto-create the table if it doesn't exist
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
        logger.warning(f"Failed to save MCP event {event_type}: {e}")
