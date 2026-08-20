"""Entrypoint for running the LiveKit MCP Server."""

import logging
import sys

import uvicorn

from livekit_mcp.config import get_settings
from livekit_mcp.server import create_app

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("livekit_mcp")

# ASGI application instance for uvicorn
app = create_app()


def run() -> None:
    """Run the MCP server with Uvicorn."""
    settings = get_settings()
    logger.info(
        "Starting LiveKit MCP Server on http://%s:%d (auth_enabled=%s, env=%s)",
        settings.host,
        settings.port,
        settings.auth_enabled,
        settings.environment,
    )
    uvicorn.run(
        "livekit_mcp.main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
