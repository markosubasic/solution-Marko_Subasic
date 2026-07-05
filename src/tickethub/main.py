import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from tickethub.config import settings
from tickethub.routers import tickets
from tickethub.sync import periodic_sync, run_sync

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await run_sync()
    except Exception:
        logger.exception("Initial sync from DummyJSON failed")

    sync_task = None
    if settings.sync_interval_seconds > 0:
        sync_task = asyncio.create_task(periodic_sync(settings.sync_interval_seconds))

    yield

    if sync_task is not None:
        sync_task.cancel()


app = FastAPI(title="TicketHub", version="1.0.0", lifespan=lifespan)

app.include_router(tickets.router)
