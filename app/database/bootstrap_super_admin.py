"""Operator-only bootstrap of an already-onboarded Firebase identity. No public route."""

import argparse
import asyncio
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database import models as m
from app.database.session import async_session, close_db


async def bootstrap(uid):
    try:
        async with async_session() as session:
            async with session.begin():
                user = await session.scalar(
                    select(m.User).where(m.User.firebase_uid == uid).with_for_update()
                )
                if user is None or user.status != "active":
                    raise RuntimeError("First onboard this Firebase identity through the API.")
                role = await session.scalar(select(m.Role).where(m.Role.code == "super_admin"))
                await session.execute(
                    insert(m.UserRole)
                    .values(user_id=user.id, role_id=role.id)
                    .on_conflict_do_nothing()
                )
                session.add(
                    m.AuditEvent(
                        action="bootstrap_super_admin",
                        target_type="user",
                        target_id=user.id,
                        outcome="success",
                        request_id=str(uuid4()),
                        event_metadata={},
                    )
                )
    finally:
        await close_db()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firebase-uid", required=True)
    asyncio.run(bootstrap(parser.parse_args().firebase_uid))
