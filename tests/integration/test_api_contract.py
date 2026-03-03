from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERAPI_DIR = REPO_ROOT / "renderapi"
if str(RENDERAPI_DIR) not in sys.path:
    sys.path.insert(0, str(RENDERAPI_DIR))

from app.main import app

client = TestClient(app)


def assert_success(resp_json: dict) -> None:
    assert resp_json["code"] == 0
    assert "request_id" in resp_json
    assert isinstance(resp_json["data"], dict)


def test_health() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert_success(body)
    assert body["data"]["status"] == "healthy"


def test_markitdown_contract() -> None:
    res = client.post(
        "/api/v1/tools/markitdown/execute",
        json={
            "payload": {
                "text": "# Title",
                "format_mode": "enhanced",
                "use_plugins": False,
            }
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert_success(body)
    assert body["data"]["tool"] == "markitdown"
    assert body["data"]["source"] == "inline-text"
    assert body["data"]["format_mode"] == "enhanced"
    assert "# Title" in body["data"]["markdown"]


def test_markitdown_upload_contract() -> None:
    res = client.post(
        "/api/v1/tools/markitdown/execute",
        data={"format_mode": "strict", "use_plugins": "false"},
        files={"file": ("demo.txt", b"# Upload Title\n", "text/plain")},
    )
    assert res.status_code == 200
    body = res.json()
    assert_success(body)
    assert body["data"]["tool"] == "markitdown"
    assert body["data"]["source"] == "upload:demo.txt"
    assert body["data"]["format_mode"] == "strict"
    assert "# Upload Title" in body["data"]["markdown"]


def test_markitdown_upload_rejects_large_file() -> None:
    large_bytes = b"a" * (10 * 1024 * 1024 + 1)
    res = client.post(
        "/api/v1/tools/markitdown/execute",
        data={"format_mode": "raw", "use_plugins": "false"},
        files={"file": ("too-large.txt", large_bytes, "text/plain")},
    )
    assert res.status_code == 413
    body = res.json()
    assert body["code"] == 41300
    assert body["message"] == "Uploaded file is too large. Max size is 10MB."
    assert "request_id" in body
