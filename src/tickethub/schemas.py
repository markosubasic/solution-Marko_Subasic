from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketStatus(str, Enum):
    open = "open"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority
    assignee: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assignee: str | None = None


class TicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    description: str | None = None

    @field_validator("description")
    @classmethod
    def truncate_description(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 100:
            return value[:97] + "..."
        return value


class TicketDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TicketStatus
    priority: TicketPriority
    assignee: str | None
    created_at: datetime
    updated_at: datetime
    raw_source: dict[str, Any] | None


class TicketListResponse(BaseModel):
    items: list[TicketListItem]
    total: int
    limit: int
    offset: int


class StatsResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
