import asyncio
from datetime import date, datetime
from typing import Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AKSHARE_ENABLE, INDEX_CODES
from app.database import async_session
from app.models.stock import DailyBar, IndexBar, Stock


class StockService:
    def __init__(self):
        self._quote_cache: dict = {}
        self._cache_time: Optional[datetime] = None

    async def _run_akshare(self, func, *args, **kwargs):
        if not AKSHARE_ENABLE:
            return pd.DataFrame()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

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
        import akshare as ak
        df = await self._run_akshare(ak.stock_info_a_code_name)
        if df.empty:
            return
        for _, row in df.iterrows():
            existing = await db.execute(
                select(Stock).where(Stock.code == str(row["code"]))
            )
            if not existing.scalar_one_or_none():
                db.add(Stock(code=str(row["code"]), name=str(row["name"])))
        await db.commit()

    async def get_realtime_quotes(self, codes: Optional[list[str]] = None) -> list[dict]:
        import akshare as ak
        df = await self._run_akshare(ak.stock_zh_a_spot)
        if df.empty:
            return []
        df = df.rename(columns={
            "代码": "code", "名称": "name", "最新价": "price",
            "涨跌额": "change", "涨跌幅": "change_pct",
            "今开": "open", "最高": "high", "最低": "low",
            "成交量": "volume", "成交额": "amount",
        })
        records = df.to_dict(orient="records")
        result = []
        for r in records:
            item = {
                "code": str(r.get("code", "")),
                "name": str(r.get("name", "")),
                "price": float(r.get("price", 0) or 0),
                "change": float(r.get("change", 0) or 0),
                "change_pct": float(r.get("change_pct", 0) or 0),
                "open": float(r.get("open", 0) or 0),
                "high": float(r.get("high", 0) or 0),
                "low": float(r.get("low", 0) or 0),
                "volume": float(r.get("volume", 0) or 0),
                "amount": float(r.get("amount", 0) or 0),
            }
            result.append(item)
        if codes:
            code_set = set(codes)
            result = [r for r in result if r["code"] in code_set]
        return result

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
        return await self._fetch_bars_from_akshare(code, start, end)

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

    async def _fetch_bars_from_akshare(self, code: str, start: Optional[str], end: Optional[str]) -> list[dict]:
        import akshare as ak
        adjusted = "qfq"
        df = await self._run_akshare(ak.stock_zh_a_hist, code, period="daily",
                                      start_date=start or "20200101", end_date=end or datetime.now().strftime("%Y%m%d"),
                                      adjust=adjusted)
        if df.empty:
            return []
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume", "成交额": "amount"
        })
        records = df.to_dict(orient="records")
        return [
            {"date": str(r.get("date", "")), "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"]),
             "volume": float(r.get("volume", 0) or 0), "amount": float(r.get("amount", 0) or 0)}
            for r in records
        ]

    async def get_index_bars(self, index_code: str, period: str = "daily") -> list[dict]:
        import akshare as ak
        df = await self._run_akshare(ak.stock_zh_index_daily, symbol=f"sh{index_code}" if index_code.startswith("0") else f"sz{index_code}")
        if df.empty:
            return []
        df = df.rename(columns={
            "date": "date", "open": "open", "high": "high",
            "low": "low", "close": "close", "volume": "volume"
        })
        records = df.to_dict(orient="records")
        return [
            {"date": str(r.get("date", "")), "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"]), "volume": float(r.get("volume", 0) or 0)}
            for r in records
        ]


stock_service = StockService()
