from sqlalchemy import select

from app.database import models as m
from app.services.common import get, now, page, row


async def list_notifications(ctx, data, **filters):
    query = select(m.Notification).where(m.Notification.user_id == ctx.user.id)
    if filters.get("unread") is True:
        query = query.where(m.Notification.read_at.is_(None))
    if filters.get("unread") is False:
        query = query.where(m.Notification.read_at.is_not(None))
    return await page(ctx, m.Notification, query, filters)


async def read_notification(ctx, data, notification_id):
    obj = await get(ctx, m.Notification, notification_id, True)
    ctx.own(obj.user_id)
    obj.read_at = obj.read_at or now()
    await ctx.session.flush()
    return row(obj)
