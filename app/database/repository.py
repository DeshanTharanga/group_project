"""Async persistence primitives. Services supply authorized queries and own transactions."""

from sqlalchemy import func, select

from app.core.errors import require


def row(obj):
    if obj is None:
        return None
    return {
        c.name: getattr(obj, "event_metadata" if c.name == "metadata" else c.name)
        for c in obj.__table__.columns
    }


async def get(ctx, model, key, lock=False):
    pk = list(model.__table__.primary_key)[0]
    query = select(model).where(pk == key)
    if lock:
        query = query.with_for_update(read=lock == "share")
    obj = await ctx.session.scalar(query)
    require(obj is not None, "Record not found.", 404, "NOT_FOUND")
    return obj


async def add(ctx, model, **values):
    obj = model(**values)
    ctx.session.add(obj)
    await ctx.session.flush()
    return obj


async def page(ctx, model, query=None, filters=None):
    query = query if query is not None else select(model)
    filters = filters or {}
    for key in ("status", "type", "role", "organization_id", "action", "request_id"):
        if filters.get(key) is not None and hasattr(model, key):
            query = query.where(getattr(model, key) == filters[key])
    datecol = next(
        (
            getattr(model, k)
            for k in (
                "scheduled_for",
                "measured_at",
                "recorded_at",
                "created_at",
                "submitted_at",
                "received_at",
            )
            if hasattr(model, k)
        ),
        None,
    )
    if datecol is not None:
        if filters.get("from"):
            query = query.where(datecol >= filters["from"])
        if filters.get("to"):
            query = query.where(datecol <= filters["to"])
    if filters.get("from") and filters.get("to"):
        require(filters["from"] <= filters["to"], "The period is invalid.", 422, "VALIDATION_ERROR")
    total = await ctx.session.scalar(
        select(func.count()).select_from(query.order_by(None).subquery())
    )
    p, size = filters.get("page", 1), filters.get("page_size", 20)
    ordering = [datecol.desc()] if datecol is not None else []
    ordering += [c.desc() for c in model.__table__.primary_key]
    objects = list(
        await ctx.session.scalars(query.order_by(*ordering).offset((p - 1) * size).limit(size))
    )
    return {"items": [row(o) for o in objects], "page": p, "page_size": size, "total": total}
