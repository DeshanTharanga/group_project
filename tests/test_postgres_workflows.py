import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from uuid import UUID

import pytest
from PIL import Image
from sqlalchemy import func, select

from app.database import models as m
from app.workers.tasks.maintenance import medication_work

pytestmark = pytest.mark.integration


def ok(response, status=200):
    assert response.status_code == status, response.text
    return response.json() if status != 204 else None


async def doctor_order(api, quantity=10):
    pid = str(api.users["patient"].id)
    grant = ok(
        await api.call(
            "POST",
            "/api/v1/access-grants",
            json={
                "doctor_reference": api.references["doctor"],
                "categories": [
                    "prescriptions",
                    "adherence",
                    "history_allergies",
                    "measurements_vaccinations",
                    "reports",
                ],
                "duration_hours": 24,
                "allow_consultation": True,
            },
        ),
        201,
    )
    queue = ok(await api.call("GET", "/api/v1/me/patient-queue", role="doctor"))
    assert any(r["patient"]["patient_user_id"] == pid for r in queue["items"])
    consultation = ok(
        await api.call(
            "POST", "/api/v1/consultations", role="doctor", json={"grant_id": grant["grant"]["id"]}
        ),
        201,
    )
    p = ok(
        await api.call(
            "POST",
            f"/api/v1/patients/{pid}/prescriptions",
            role="doctor",
            json={
                "consultation_id": consultation["id"],
                "items": [
                    {
                        "medicine_name_snapshot": "Synthetic medicine",
                        "dose_text": "Synthetic instruction",
                        "frequency": "Daily",
                        "quantity": quantity,
                        "quantity_unit": "tablet",
                        "is_prn": False,
                    }
                ],
            },
        ),
        201,
    )
    p = ok(
        await api.call(
            "POST", f"/api/v1/prescriptions/{p['prescription']['id']}/issue", role="doctor"
        )
    )
    return p, grant, consultation


async def confirmed_share(api, p):
    shared = ok(
        await api.call(
            "POST", "/api/v1/prescription-shares", json={"prescription_id": p["prescription"]["id"]}
        ),
        201,
    )
    claimed = ok(
        await api.call(
            "POST",
            "/api/v1/prescription-shares/claim",
            role="pharmacist",
            json={
                "claim_token": shared["claim_token"],
                "organization_id": str(api.orgs["pharmacist"].id),
            },
        )
    )
    assert claimed["pharmacist"]["user_id"] == str(api.users["pharmacist"].id)
    share = ok(
        await api.call("POST", f"/api/v1/prescription-shares/{shared['share']['id']}/confirm")
    )
    return share["share"]["id"]


async def test_prescription_scope_and_response_projections(api):
    p, grant, consult = await doctor_order(api)
    pid = str(api.users["patient"].id)
    values = ok(await api.call("GET", f"/api/v1/patients/{pid}/prescriptions"))
    assert values["items"][0]["prescription"]["id"] == p["prescription"]["id"]
    assert "firebase_uid" not in ok(await api.call("GET", "/api/v1/me"))["user"]
    ok(
        await api.call(
            "POST",
            f"/api/v1/access-grants/{grant['grant']['id']}/revoke",
            json={"reason": "Synthetic revoke"},
        ),
        201,
    )
    assert (
        await api.call("GET", f"/api/v1/prescriptions/{p['prescription']['id']}", role="doctor")
    ).status_code == 403
    assert (
        await api.call("GET", f"/api/v1/prescriptions/{p['prescription']['id']}", role="admin")
    ).status_code == 403


async def test_concurrent_dispensing_cannot_overfill(api):
    p, _, _ = await doctor_order(api)
    share_id = await confirmed_share(api, p)
    payload = {
        "share_id": share_id,
        "organization_id": str(api.orgs["pharmacist"].id),
        "items": [
            {"prescription_item_id": p["items"][0]["id"], "quantity": 7, "quantity_unit": "tablet"}
        ],
    }

    async def dispense(key):
        return await api.call(
            "POST",
            "/api/v1/dispensing-events",
            role="pharmacist",
            json=payload,
            headers={"Idempotency-Key": key},
        )

    responses = await asyncio.gather(dispense("synthetic-a"), dispense("synthetic-b"))
    assert sorted(r.status_code for r in responses) == [201, 409]
    key = "synthetic-a" if responses[0].status_code == 201 else "synthetic-b"
    winner = next(r.json() for r in responses if r.status_code == 201)
    replay = ok(await dispense(key), 201)
    assert replay["event"]["id"] == winner["event"]["id"]
    projection = ok(
        await api.call(
            "GET", f"/api/v1/prescription-shares/{share_id}/prescription", role="pharmacist"
        )
    )
    assert Decimal(str(projection["items"][0]["remaining_quantity"])) == 3
    reverse = ok(
        await api.call(
            "POST",
            f"/api/v1/dispensing-events/{winner['event']['id']}/reversal",
            role="pharmacist",
            json={"reason": "Synthetic reversal"},
            headers={"Idempotency-Key": "reverse-once"},
        ),
        201,
    )
    assert reverse["event"]["reversal_of_id"] == winner["event"]["id"]
    own = ok(await api.call("GET", "/api/v1/me/dispensing-events", role="pharmacist"))
    assert all("patient_user_id" not in event for event in own["items"])


async def test_patient_source_cannot_be_shared(api):
    pid = str(api.users["patient"].id)
    p = ok(
        await api.call(
            "POST",
            f"/api/v1/patients/{pid}/prescriptions",
            json={
                "items": [
                    {
                        "medicine_name_snapshot": "Synthetic",
                        "dose_text": "Synthetic",
                        "frequency": "Daily",
                        "is_prn": False,
                    }
                ]
            },
        ),
        201,
    )
    ok(await api.call("POST", f"/api/v1/prescriptions/{p['prescription']['id']}/confirm"))
    response = await api.call(
        "POST", "/api/v1/prescription-shares", json={"prescription_id": p["prescription"]["id"]}
    )
    assert response.status_code == 409


async def test_worker_deduplication_and_latest_response_adherence(api):
    p, _, _ = await doctor_order(api)
    pid = str(api.users["patient"].id)
    timestamp = datetime.now(UTC).replace(second=0, microsecond=0)
    t = (timestamp - timedelta(minutes=1)).time().isoformat(timespec="minutes")
    schedule = ok(
        await api.call(
            "POST",
            f"/api/v1/patients/{pid}/medication-schedules",
            json={
                "prescription_item_id": p["items"][0]["id"],
                "timezone": "UTC",
                "starts_at": (timestamp - timedelta(hours=1)).isoformat(),
                "times": [t],
                "confirmed": True,
            },
        ),
        201,
    )
    async with api.sessions() as session:
        async with session.begin():
            await medication_work(session, UUID(schedule["schedule"]["id"]))
        async with session.begin():
            await medication_work(session, UUID(schedule["schedule"]["id"]))
        count = await session.scalar(
            select(func.count())
            .select_from(m.Notification)
            .where(
                m.Notification.user_id == api.users["patient"].id,
                m.Notification.notification_type == "medication",
            )
        )
        assert count == 1
    occurrences = ok(await api.call("GET", f"/api/v1/patients/{pid}/dose-occurrences"))
    due = next(o for o in occurrences["items"] if o["status"] == "due")
    log = ok(
        await api.call(
            "POST",
            f"/api/v1/dose-occurrences/{due['id']}/responses",
            json={"response": "taken", "reported_taken_at": timestamp.isoformat()},
            headers={"Idempotency-Key": "synthetic-dose-response"},
        ),
        201,
    )
    ok(
        await api.call(
            "POST",
            f"/api/v1/medication-logs/{log['id']}/corrections",
            json={"response": "skipped", "correction_reason": "Synthetic correction"},
            headers={"Idempotency-Key": "synthetic-dose-correction"},
        ),
        201,
    )
    summary = ok(
        await api.call(
            "GET",
            f"/api/v1/patients/{pid}/adherence",
            params={
                "from": (timestamp - timedelta(hours=2)).isoformat(),
                "to": (timestamp + timedelta(minutes=5)).isoformat(),
            },
        )
    )
    assert summary["taken"] == 0 and summary["skipped"] == 1 and summary["eligible"] == 1


async def test_lab_report_consumes_request_once_and_filters_private_storage(api):
    pid = str(api.users["patient"].id)
    request = ok(
        await api.call(
            "POST",
            "/api/v1/lab-upload-requests",
            json={"laboratory_id": str(api.orgs["lab_staff"].id)},
        ),
        201,
    )
    resolved = ok(
        await api.call(
            "POST",
            "/api/v1/lab-upload-requests/resolve",
            role="lab_staff",
            json={
                "request_token": request["request_token"],
                "laboratory_id": str(api.orgs["lab_staff"].id),
            },
        )
    )
    b = BytesIO()
    Image.new("RGB", (2, 2)).save(b, format="PNG")
    document = ok(
        await api.call(
            "POST",
            f"/api/v1/patients/{pid}/documents",
            role="lab_staff",
            files={"file": ("synthetic.png", b.getvalue(), "image/png")},
            data={"document_type": "report", "upload_request_id": resolved["request_id"]},
        ),
        201,
    )
    assert "storage_key" not in document
    payload = {
        "document_id": document["id"],
        "upload_request_id": resolved["request_id"],
        "report_type": "Synthetic",
        "lab_reference": f"SYNTHETIC-{document['id']}",
    }
    report = ok(
        await api.call(
            "POST",
            f"/api/v1/patients/{pid}/reports",
            role="lab_staff",
            json=payload,
            headers={"Idempotency-Key": "publish-synthetic"},
        ),
        201,
    )
    assert report["source"] == "laboratory"
    replay = ok(
        await api.call(
            "POST",
            f"/api/v1/patients/{pid}/reports",
            role="lab_staff",
            json=payload,
            headers={"Idempotency-Key": "publish-synthetic"},
        ),
        201,
    )
    assert replay["id"] == report["id"]
    duplicate = await api.call(
        "POST",
        f"/api/v1/patients/{pid}/reports",
        role="lab_staff",
        json=payload,
        headers={"Idempotency-Key": "publish-another"},
    )
    assert duplicate.status_code == 409
    notification = ok(await api.call("GET", "/api/v1/me/notifications"))
    assert notification["total"] >= 1
