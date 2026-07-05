import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from tickethub.auth import create_access_token
from tickethub.cache import stats_cache
from tickethub.database import Base, get_session
from tickethub.main import app
from tickethub.models import Ticket


@pytest.fixture(autouse=True)
def clear_cache():
    stats_cache.clear()
    yield
    stats_cache.clear()


@pytest.fixture
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session


@pytest.fixture
async def client(engine):
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session():
        async with maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    token = create_access_token("testuser")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def seeded_tickets(session):
    tickets = [
        Ticket(
            id=1,
            title="Fix login bug",
            description="Users cannot log in with valid credentials",
            status="open",
            priority="medium",
            assignee="emilys",
            raw_source={"id": 1, "todo": "Fix login bug", "completed": False, "userId": 1},
        ),
        Ticket(
            id=2,
            title="Update documentation",
            description="d" * 150,
            status="closed",
            priority="high",
            assignee="michaelw",
        ),
        Ticket(id=3, title="Add dark mode", status="open", priority="low"),
    ]
    session.add_all(tickets)
    await session.commit()
    return tickets
