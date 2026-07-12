import asyncio
import logging

from app.config import AKSHARE_ENABLE
from app.database import async_session

logger = logging.getLogger(__name__)


async def init_app_data():
    if not AKSHARE_ENABLE:
        logger.info("akshare 已禁用，跳过数据初始化")
        return
    from app.models.stock import Stock
    from app.services.stock_service import stock_service
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(select(Stock).limit(1))
        if result.scalar_one_or_none():
            logger.info("股票数据已存在，跳过初始化")
            return

    logger.info("开始初始化股票数据...")
    async with async_session() as db:
        await stock_service.refresh_stock_list(db)
    logger.info("股票数据初始化完成")
