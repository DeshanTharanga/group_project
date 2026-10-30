"""A replay never bypasses current account, consent or organization authorization."""

from uuid import UUID

from app.core.errors import require
from app.database import models as m
from app.services.common import get, membership, patient_access, professional


async def authorize_replay(ctx, operation, body, params):
    if body is None:
        if params.get("prescription_id"):
            from app.modules.prescriptions.service import readable, writable

            p = await readable(ctx, params["prescription_id"])
            await writable(ctx, p)
        return
    if operation in ("dispense", "shared_prescription"):
        from app.modules.dispensing.service import authorized_share

        share_id = body["event"]["share_id"] if operation == "dispense" else params["share_id"]
        await authorized_share(ctx, UUID(str(share_id)))
        return
    if operation == "reverse_dispensing":
        event = await get(ctx, m.DispensingEvent, UUID(body["event"]["id"]))
        require(event.pharmacist_user_id == ctx.user.id)
        await membership(ctx, event.organization_id, "pharmacist")
        return
    if ctx.client:
        from app.modules.integrations.service import laboratory

        await laboratory(ctx, ctx.client.organization_id)
        if body.get("report_id"):
            report = await get(ctx, m.Report, UUID(body["report_id"]))
            require(report.laboratory_id == ctx.client.organization_id)
        return
    if operation in ("publish_report", "replace_report", "withdraw_report"):
        from app.modules.documents.service import report_access

        report = await get(ctx, m.Report, UUID(body["id"]))
        await report_access(ctx, report)
        return
    if (
        "prescription" in body
        and isinstance(body["prescription"], dict)
        and "patient_user_id" in body["prescription"]
    ):
        p = await get(ctx, m.Prescription, UUID(body["prescription"]["id"]))
        from app.modules.prescriptions.service import writable

        await writable(ctx, p)
        return
    category = "history_allergies"
    if "measurement" in operation or "vaccination" in operation:
        category = "measurements_vaccinations"
    if "prescription" in operation:
        category = "prescriptions"
    if any(w in operation for w in ("schedule", "occurrence", "log", "adherence")):
        category = "adherence"
    if "patient_user_id" in body:
        pid = UUID(body["patient_user_id"])
        await patient_access(ctx, pid, category)
    elif params.get("patient_id"):
        await patient_access(ctx, params["patient_id"], category)
    if operation.startswith(("admin_", "decide_", "set_user_", "retry_job", "create_medicine")):
        ctx.admin()
    if operation in ("assign_admin", "revoke_admin", "revoke_client", "suspend_client"):
        from app.modules.audit.service import privileged

        privileged(ctx)
    if "template" in operation:
        await professional(ctx)
