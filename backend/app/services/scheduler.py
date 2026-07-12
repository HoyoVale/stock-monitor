from datetime import datetime, time

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import TRADING_ONLY, REFRESH_INTERVAL

scheduler = AsyncIOScheduler()


def is_trading_time() -> bool:
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    try:
        from chinese_calendar import is_workday
        if not is_workday(now.date()):
            return False
    except ImportError:
        pass
    t = now.time()
    return (time(9, 30) <= t <= time(11, 30)) or (time(13, 0) <= t <= time(15, 0))


async def refresh_quotes_job():
    if TRADING_ONLY and not is_trading_time():
        return
    from app.services.stock_service import stock_service
    from app.database import async_session
    async with async_session() as db:
        quotes = await stock_service.get_realtime_quotes()
        if not TRADING_ONLY:
            await stock_service.refresh_stock_list(db)
    return quotes


def start_jobs():
    scheduler.add_job(refresh_quotes_job, "interval", seconds=REFRESH_INTERVAL, id="refresh_quotes")


def stop_jobs():
    scheduler.shutdown(wait=False)
