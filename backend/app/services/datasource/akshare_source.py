import asyncio
from datetime import datetime
from typing import Optional

import pandas as pd

from backend.app.config import AKSHARE_ENABLE
from backend.app.services.datasource.base import BaseDataSource


class AkshareDataSource(BaseDataSource):
    """Data source implementation using akshare library."""

    name: str = "akshare"

    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous akshare function in a thread pool."""
        if not AKSHARE_ENABLE:
            return pd.DataFrame()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def get_realtime_quotes(self, codes: Optional[list[str]] = None) -> list[dict]:
        import akshare as ak
        df = await self._run_sync(ak.stock_zh_a_spot)
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

    async def get_daily_bars(
        self, code: str, start: Optional[str] = None, end: Optional[str] = None, period: str = "daily"
    ) -> list[dict]:
        import akshare as ak
        adjusted = "qfq"
        df = await self._run_sync(
            ak.stock_zh_a_hist, code, period="daily",
            start_date=start or "20200101",
            end_date=end or datetime.now().strftime("%Y%m%d"),
            adjust=adjusted,
        )
        if df.empty:
            return []
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume", "成交额": "amount",
        })
        records = df.to_dict(orient="records")
        return [
            {
                "date": str(r.get("date", "")),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r.get("volume", 0) or 0),
                "amount": float(r.get("amount", 0) or 0),
            }
            for r in records
        ]

    async def get_index_bars(self, index_code: str, period: str = "daily") -> list[dict]:
        import akshare as ak
        symbol = f"sh{index_code}" if index_code.startswith("0") else f"sz{index_code}"
        df = await self._run_sync(ak.stock_zh_index_daily, symbol=symbol)
        if df.empty:
            return []
        df = df.rename(columns={
            "date": "date", "open": "open", "high": "high",
            "low": "low", "close": "close", "volume": "volume",
        })
        records = df.to_dict(orient="records")
        return [
            {
                "date": str(r.get("date", "")),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r.get("volume", 0) or 0),
            }
            for r in records
        ]

    async def refresh_stock_list(self, db) -> None:
        import akshare as ak
        from sqlalchemy import select
        from backend.app.models.stock import Stock

        df = await self._run_sync(ak.stock_info_a_code_name)
        if df.empty:
            return
        for _, row in df.iterrows():
            existing = await db.execute(
                select(Stock).where(Stock.code == str(row["code"]))
            )
            if not existing.scalars().first():
                db.add(Stock(code=str(row["code"]), name=str(row["name"])))
        await db.commit()

    async def health_check(self) -> bool:
        if not AKSHARE_ENABLE:
            return False
        try:
            import akshare
            return True
        except ImportError:
            return False
