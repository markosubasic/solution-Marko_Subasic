from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.auth import get_current_user
from tickethub.cache import stats_cache
from tickethub.database import get_session
from tickethub.models import Ticket
from tickethub.schemas import (
    TicketCreate,
    TicketDetail,
    TicketListResponse,
    TicketPriority,
    TicketStatus,
    TicketUpdate,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


async def paginated_response(
    session: AsyncSession, query: Select, limit: int, offset: int
) -> TicketListResponse:
    total = (
        await session.execute(select(func.count()).select_from(query.subquery()))
    ).scalar_one()
    result = await session.execute(query.order_by(Ticket.id).limit(limit).offset(offset))
    return TicketListResponse(
        items=result.scalars().all(), total=total, limit=limit, offset=offset
    )


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    query = select(Ticket)
    if status is not None:
        query = query.where(Ticket.status == status.value)
    if priority is not None:
        query = query.where(Ticket.priority == priority.value)
    return await paginated_response(session, query, limit, offset)


@router.get("/search", response_model=TicketListResponse)
async def search_tickets(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    query = select(Ticket).where(Ticket.title.ilike(f"%{q}%"))
    return await paginated_response(session, query, limit, offset)


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketDetail, status_code=http_status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    session: AsyncSession = Depends(get_session),
    _user: str = Depends(get_current_user),
):
    ticket = Ticket(**payload.model_dump(mode="json"))
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    stats_cache.clear()
    return ticket


@router.patch("/{ticket_id}", response_model=TicketDetail)
async def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    session: AsyncSession = Depends(get_session),
    _user: str = Depends(get_current_user),
):
    ticket = await session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for field, value in payload.model_dump(mode="json", exclude_unset=True).items():
        setattr(ticket, field, value)
    await session.commit()
    await session.refresh(ticket)
    stats_cache.clear()
    return ticket
