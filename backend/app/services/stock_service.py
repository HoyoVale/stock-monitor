from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import INDEX_CODES, DS_FAILURE_THRESHOLD
from app.database import async_session
from app.models.stock import DailyBar, IndexBar, Stock
from app.services.datasource import get_datasource
from app.services.datasource.base import BaseDataSource


class StockService:
    def __init__(self):
        self._datasource: Optional[BaseDataSource] = None
        self._quote_cache: dict = {}
        self._cache_time: Optional[datetime] = None

    def _get_ds(self) -> BaseDataSource:
        """Lazy-load and cache the data source instance."""
        if self._datasource is None:
            self._datasource = get_datasource()
            self._datasource._max_failures = DS_FAILURE_THRESHOLD
        return self._datasource

    async def get_all_stocks(self, db: AsyncSession) -> list[Stock]:
        result = await db.execute(select(Stock).order_by(Stock.code))
        return list(result.scalars().all())

    async def search_stocks(self, db: AsyncSession, keyword: str) -> list[Stock]:
        stmt = select(Stock).where(
            Stock.code.like(f"%{keyword}%") | Stock.name.like(f"%{keyword}%")
        ).order_by(Stock.code).limit(50)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def refresh_stock_list(self, db: AsyncSession):
        ds = self._get_ds()
        await ds._try_with_fallback("refresh_stock_list", db)

    async def get_realtime_quotes(self, codes: Optional[list[str]] = None) -> list[dict]:
        ds = self._get_ds()
        return await ds._try_with_fallback("get_realtime_quotes", codes)

    async def get_index_quotes(self) -> list[dict]:
        quotes = await self.get_realtime_quotes()
        index_codes = set(INDEX_CODES.values())
        return [q for q in quotes if q["code"] in index_codes]

    async def get_daily_bars(
        self, code: str, start: Optional[str] = None, end: Optional[str] = None, period: str = "daily"
    ) -> list[dict]:
        db_bars = await self._get_bars_from_db(code, start, end)
        if db_bars:
            return db_bars
        ds = self._get_ds()
        return await ds._try_with_fallback("get_daily_bars", code, start, end, period)

    async def _get_bars_from_db(self, code: str, start: Optional[str], end: Optional[str]) -> list[dict]:
        async with async_session() as db:
            stmt = select(DailyBar).where(DailyBar.code == code).order_by(DailyBar.date)
            if start:
                stmt = stmt.where(DailyBar.date >= date.fromisoformat(start))
            if end:
                stmt = stmt.where(DailyBar.date <= date.fromisoformat(end))
            result = await db.execute(stmt)
            bars = result.scalars().all()
            if bars:
                return [
                    {"date": b.date.isoformat(), "open": b.open, "high": b.high,
                     "low": b.low, "close": b.close, "volume": b.volume, "amount": b.amount}
                    for b in bars
                ]
            return []

    async def get_index_bars(self, index_code: str, period: str = "daily") -> list[dict]:
        ds = self._get_ds()
        return await ds._try_with_fallback("get_index_bars", index_code, period)

    async def datasource_health(self) -> dict:
        """Return health status of all configured data sources."""
        ds = self._get_ds()
        result = {
            "primary": {
                "name": ds.name,
                "available": await ds.health_check(),
                "failures": ds._failure_count,
            }
        }
        if ds._backup:
            result["backup"] = {
                "name": ds._backup.name,
                "available": await ds._backup.health_check(),
                "failures": ds._backup._failure_count,
            }
        return result


stock_service = StockService()
