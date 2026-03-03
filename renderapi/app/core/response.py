from __future__ import annotations

import uuid
from typing import Any


def ok_response(data: Any = None, message: str = "ok", request_id: str | None = None) -> dict:
    return {
        "code": 0,
        "message": message,
        "data": data if data is not None else {},
        "request_id": request_id or str(uuid.uuid4()),
    }


def error_response(code: int, message: str, request_id: str | None = None) -> dict:
    return {
        "code": code,
        "message": message,
        "data": {},
        "request_id": request_id or str(uuid.uuid4()),
    }
