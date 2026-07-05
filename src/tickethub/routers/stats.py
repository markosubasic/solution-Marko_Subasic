from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.cache import stats_cache
from tickethub.database import get_session
from tickethub.models import Ticket
from tickethub.schemas import StatsResponse

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(session: AsyncSession = Depends(get_session)):
    cached = stats_cache.get("stats")
    if cached is not None:
        return cached

    total = (await session.execute(select(func.count()).select_from(Ticket))).scalar_one()
    by_status = await session.execute(
        select(Ticket.status, func.count()).group_by(Ticket.status)
    )
    by_priority = await session.execute(
        select(Ticket.priority, func.count()).group_by(Ticket.priority)
    )
    stats = StatsResponse(
        total=total,
        by_status=dict(by_status.all()),
        by_priority=dict(by_priority.all()),
    )
    stats_cache.set("stats", stats)
    return stats
