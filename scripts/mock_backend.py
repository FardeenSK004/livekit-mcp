"""Lightweight Mock MantraAssist Backend (:5500) for testing doctor availability."""

from datetime import datetime
import json
import logging
from uvicorn import run
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mock_backend")

# Sample mock doctors database
SAMPLE_DOCTORS = [
    {
        "user_id": 101,
        "name": "Dr. Ananya Sharma",
        "department": "Cardiology",
        "specialization": "Cardiology",
        "available_slots": [
            "04:30 - 05:30",  # 10:00 AM - 11:00 AM IST / 12:30 AM - 01:30 AM EDT
            "06:00 - 07:00",  # 11:30 AM - 12:30 PM IST / 02:00 AM - 03:00 AM EDT
            "14:00 - 15:00",  # 07:30 PM - 08:30 PM IST / 10:00 AM - 11:00 AM EDT
        ],
    },
    {
        "user_id": 104,
        "name": "Dr. Rajesh Kumar",
        "department": "Dermatology",
        "specialization": "Dermatology",
        "available_slots": [
            "05:00 - 06:00",  # 10:30 AM - 11:30 AM IST
            "07:30 - 08:30",  # 01:00 PM - 02:00 PM IST
            "15:00 - 16:00",  # 11:00 AM - 12:00 PM EDT
        ],
    },
    {
        "user_id": 108,
        "name": "Dr. Vikram Sethi",
        "department": "Orthopedics",
        "specialization": "Orthopedics",
        "available_slots": [
            "08:30 - 09:30",
            "10:00 - 11:00",
        ],
    },
]


async def availability_endpoint(request: Request) -> JSONResponse:
    """Handle GET or POST /api/v1/providers/availability."""
    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = {}
        org_id = body.get("org_id", 68)
        date_str = body.get("date", "")
        datetime_str = body.get("datetime", "")
        doc_name = body.get("doc_name", "")
        department = body.get("department", "")
    else:
        org_id = request.query_params.get("org_id", "68")
        date_str = request.query_params.get("date", "")
        datetime_str = request.query_params.get("datetime", "")
        doc_name = request.query_params.get("doc_name", "")
        department = request.query_params.get("department", "")

    logger.info(
        "📥 [MOCK BACKEND] Received request: org_id=%s, date=%s, datetime=%s, doc_name='%s', department='%s'",
        org_id,
        date_str,
        datetime_str,
        doc_name,
        department,
    )

    filtered_providers = []
    doc_filter = doc_name.lower().strip() if doc_name else ""
    dept_filter = department.lower().strip() if department else ""

    for doc in SAMPLE_DOCTORS:
        matches_doc = not doc_filter or doc_filter in doc["name"].lower()
        matches_dept = not dept_filter or dept_filter in doc["department"].lower() or dept_filter in doc["specialization"].lower()

        if matches_doc and matches_dept:
            filtered_providers.append(doc)

    response_payload = {
        "status": "success",
        "org_id": org_id,
        "date": date_str or datetime.now().strftime("%Y-%m-%d"),
        "datetime": datetime_str or datetime.now().strftime("%Y-%m-%dT00:00:00.000Z"),
        "providers": filtered_providers,
    }

    logger.info("📤 [MOCK BACKEND] Returning %d matching doctors", len(filtered_providers))
    return JSONResponse(response_payload)


routes = [
    Route("/api/v1/providers/availability", endpoint=availability_endpoint, methods=["GET", "POST"]),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    print("\n🚀 Starting Mock MantraAssist Backend on http://localhost:5500 ...")
    print("👉 Endpoint: http://localhost:5500/api/v1/providers/availability\n")
    run(app, host="0.0.0.0", port=5500)
