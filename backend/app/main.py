import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, auth, backtest, health, indices, indicators, predictions, stocks, watchlist, ws
from app.database import init_db
from app.init_data import init_app_data
from app.logging_config import configure_logging
from app.middleware import RequestLoggingMiddleware
from app.services.scheduler import start_jobs, stop_jobs

configure_logging()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动中...")
    await init_db()
    start_jobs()
    asyncio.create_task(init_app_data())
    yield
    stop_jobs()
    logger.info("已关闭")


app = FastAPI(title="股市监控系统", version="0.3.0", lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(indices.router)
app.include_router(stocks.router)
app.include_router(watchlist.router)
app.include_router(indicators.router)
app.include_router(alerts.router)
app.include_router(backtest.router)
app.include_router(predictions.router)
app.include_router(ws.router)
app.include_router(auth.router)
