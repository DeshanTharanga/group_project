"""The supplied interface is the baseline, including root-level FHIR paths."""

import importlib
import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

CONTRACT = json.loads((Path(__file__).parents[1] / "docs/contract.json").read_text())


def test_all_documented_routes_and_async_services_exist():
    schema = app.openapi()
    assert len(CONTRACT) == 124
    for op in CONTRACT:
        actual = schema["paths"][op["path"]][op["method"].lower()]
        assert str(op["status"]) in actual["responses"]
        service = importlib.import_module(f"app.modules.{op['module']}.service")
        assert inspect.iscoroutinefunction(getattr(service, op["name"]))


def test_health_does_not_require_database_or_firebase():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-request-id"]


def test_missing_identity_is_consistent_401():
    with TestClient(app) as client:
        response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert set(response.json()) == {"code", "message", "field_errors", "request_id"}


def test_cors_allows_duplicate_request_header():
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/dispensing-events",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type,Idempotency-Key",
            },
        )
    assert response.status_code == 200


def test_response_models_do_not_expose_secrets():
    schema = app.openapi()
    for name, model in schema["components"]["schemas"].items():
        if name.endswith("Input"):
            continue
        fields = model.get("properties", {})
        assert (
            not {
                "firebase_uid",
                "storage_key",
                "credential_hash",
                "claim_token_hash",
                "request_token_hash",
            }
            & fields.keys()
        )
