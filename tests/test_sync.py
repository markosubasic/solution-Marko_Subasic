import pytest

from tickethub import sync
from tickethub.models import Ticket
from tickethub.sync import sync_tickets, todo_to_ticket

USERNAMES = {5: "emilys"}


def test_completed_todo_becomes_closed_ticket():
    todo = {"id": 3, "todo": "Memorize a poem", "completed": True, "userId": 5}
    ticket = todo_to_ticket(todo, USERNAMES)
    assert ticket.id == 3
    assert ticket.title == "Memorize a poem"
    assert ticket.status == "closed"
    assert ticket.assignee == "emilys"
    assert ticket.raw_source == todo


def test_uncompleted_todo_stays_open():
    todo = {"id": 1, "todo": "Do something", "completed": False, "userId": 5}
    assert todo_to_ticket(todo, USERNAMES).status == "open"


@pytest.mark.parametrize("ticket_id,expected", [(3, "low"), (4, "medium"), (5, "high")])
def test_priority_is_derived_from_id(ticket_id, expected):
    todo = {"id": ticket_id, "todo": "t", "completed": False, "userId": 5}
    assert todo_to_ticket(todo, USERNAMES).priority == expected


def test_unknown_user_gives_no_assignee():
    todo = {"id": 1, "todo": "t", "completed": False, "userId": 999}
    assert todo_to_ticket(todo, USERNAMES).assignee is None


async def test_sync_inserts_only_new_tickets(session, monkeypatch):
    todos = [
        {"id": 1, "todo": "First", "completed": False, "userId": 5},
        {"id": 2, "todo": "Second", "completed": True, "userId": 5},
    ]

    async def fake_todos():
        return todos

    async def fake_users():
        return USERNAMES

    monkeypatch.setattr(sync.dummyjson, "fetch_todos", fake_todos)
    monkeypatch.setattr(sync.dummyjson, "fetch_users", fake_users)

    assert await sync_tickets(session) == 2
    assert await sync_tickets(session) == 0

    ticket = await session.get(Ticket, 2)
    assert ticket.status == "closed"
