import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub import dummyjson
from tickethub.database import SessionLocal
from tickethub.models import Ticket

logger = logging.getLogger(__name__)

PRIORITIES = ("low", "medium", "high")


def todo_to_ticket(todo: dict[str, Any], usernames: dict[int, str]) -> Ticket:
    return Ticket(
        id=todo["id"],
        title=todo["todo"],
        description=todo["todo"],
        status="closed" if todo["completed"] else "open",
        priority=PRIORITIES[todo["id"] % 3],
        assignee=usernames.get(todo["userId"]),
        raw_source=todo,
    )


async def sync_tickets(session: AsyncSession) -> int:
    todos = await dummyjson.fetch_todos()
    usernames = await dummyjson.fetch_users()

    existing_ids = set((await session.execute(select(Ticket.id))).scalars())
    new_tickets = [
        todo_to_ticket(todo, usernames) for todo in todos if todo["id"] not in existing_ids
    ]
    session.add_all(new_tickets)
    await session.commit()
    return len(new_tickets)


async def run_sync() -> None:
    async with SessionLocal() as session:
        added = await sync_tickets(session)
    logger.info("Sync finished, %d new tickets added", added)


async def periodic_sync(interval_seconds: int) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            await run_sync()
        except Exception:
            logger.exception("Periodic sync failed")
