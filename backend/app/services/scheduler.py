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


async def check_alerts_job():
    if TRADING_ONLY and not is_trading_time():
        return
    from sqlalchemy import select
    from app.database import async_session
    from app.models.alert import AlertRule, AlertRecord
    from app.services.stock_service import stock_service
    from app.services.notification_service import notification_service

    async with async_session() as db:
        result = await db.execute(
            select(AlertRule).where(AlertRule.enabled == True)
        )
        rules = result.scalars().all()
        if not rules:
            return

        codes = list({r.stock_code for r in rules})
        quotes = await stock_service.get_realtime_quotes(codes=codes)
        quote_map = {q["code"]: q for q in quotes}

        for rule in rules:
            quote = quote_map.get(rule.stock_code)
            if not quote or quote["price"] == 0:
                continue

            triggered = False
            direction = ""
            if rule.alert_type == "price_above" and quote["price"] >= rule.threshold:
                triggered = True
                direction = "上穿"
            elif rule.alert_type == "price_below" and quote["price"] <= rule.threshold:
                triggered = True
                direction = "下穿"

            if triggered:
                record = AlertRecord(
                    rule_id=rule.id,
                    stock_code=rule.stock_code,
                    price=quote["price"],
                    message=f"{rule.stock_code} 价格{direction}阈值 {rule.threshold}，当前价 {quote['price']}",
                )
                db.add(record)
                rule.enabled = False

                # 发送通知
                await notification_service.notify_alert(
                    stock_code=rule.stock_code,
                    stock_name=quote.get("name", ""),
                    alert_type=rule.alert_type,
                    threshold=rule.threshold,
                    current_price=quote["price"],
                )

        await db.commit()


def start_jobs():
    scheduler.add_job(refresh_quotes_job, "interval", seconds=REFRESH_INTERVAL, id="refresh_quotes")
    scheduler.add_job(check_alerts_job, "interval", seconds=60, id="check_alerts")


def stop_jobs():
    scheduler.shutdown(wait=False)
