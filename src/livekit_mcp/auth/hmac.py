import hmac
import hashlib
import json
import time
import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

def canonicalize_payload(payload: dict[str,Any]) -> str:
    if not payload:
        return "{}"
    return json.dumps(payload, separators=",", ":")

def build_signature(payload_str: str, timestamp: str, secret: str) -> str:
    data_to_sign = f"{payload_str}.{timestamp}"
    return hmac.new(
        secret.encode{"utf-8"},
        data_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def build_signed_headers(payload: dict[str, Any] | None,secret:str | None, source: str = "n8n"  )