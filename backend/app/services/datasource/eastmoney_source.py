import asyncio
from datetime import datetime
from typing import Optional

import httpx

from backend.app.services.datasource.base import BaseDataSource


class EastmoneyDataSource(BaseDataSource):
    """Data source implementation using 东方财富 (East Money) public APIs."""

    name: str = "eastmoney"

    _BASE_URL = "https://push2.eastmoney.com"
    _KLINE_URL = "https://push2his.eastmoney.com"

    def __init__(self, timeout: float = 15.0):
        super().__init__()
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def _fetch_json(self, url: str, params: dict) -> dict:
        """Fetch JSON from East Money API with error handling."""
        client = await self._get_client()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://quote.eastmoney.com/",
        }
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def get_realtime_quotes(self, codes: Optional[list[str]] = None) -> list[dict]:
        params = {
            "pn": "1",
            "pz": "5000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20",
            "_": str(int(datetime.now().timestamp() * 1000)),
        }
        if codes:
            params["fs"] = f"b:{",".join(codes)}"

        url = f"{self._BASE_URL}/api/qt/clist/get"
        data = await self._fetch_json(url, params)
        if not data or "data" not in data or data["data"] is None:
            return []

        diffs = data["data"].get("diff", [])
        result = []
        for r in diffs:
            item = {
                "code": str(r.get("f12", "")),
                "name": str(r.get("f14", "")),
                "price": float(r.get("f2", 0) or 0),
                "change": float(r.get("f4", 0) or 0),
                "change_pct": float(r.get("f3", 0) or 0),
                "open": float(r.get("f17", 0) or 0),
                "high": float(r.get("f15", 0) or 0),
                "low": float(r.get("f16", 0) or 0),
                "volume": float(r.get("f5", 0) or 0),
                "amount": float(r.get("f6", 0) or 0),
            }
            result.append(item)
        return result

    async def _resolve_market(self, code: str) -> str:
        """Determine market prefix for East Money API."""
        if code.startswith("6"):
            return "1"  # Shanghai
        elif code.startswith("0") or code.startswith("3"):
            return "0"  # Shenzhen
        elif code.startswith("4") or code.startswith("8"):
            return "0"  # Beijing
        return "0"

    async def get_daily_bars(
        self, code: str, start: Optional[str] = None, end: Optional[str] = None, period: str = "daily"
    ) -> list[dict]:
        market = await self._resolve_market(code)
        secid = f"{market}.{code}"
        period_map = {"daily": "101", "weekly": "102", "monthly": "103"}
        klt = period_map.get(period, "101")

        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "ut": "7eea3edcaed734bea9cbfce24459ed57",
            "klt": klt,
            "fqt": "1",  # 前复权
            "secid": secid,
            "beg": start or "20200101",
            "end": end or datetime.now().strftime("%Y%m%d"),
            "lmt": "10000",
            "_": str(int(datetime.now().timestamp() * 1000)),
        }

        url = f"{self._KLINE_URL}/api/qt/stock/kline/get"
        data = await self._fetch_json(url, params)
        if not data or "data" not in data or data["data"] is None:
            return []

        klines = data["data"].get("klines", [])
        result = []
        for line in klines:
            parts = line.split(",")
            if len(parts) < 7:
                continue
            result.append({
                "date": parts[0],
                "open": float(parts[1]),
                "close": float(parts[2]),
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": float(parts[5]),
                "amount": float(parts[6]),
            })
        return result

    async def get_index_bars(self, index_code: str, period: str = "daily") -> list[dict]:
        market = await self._resolve_market(index_code)
        secid = f"{market}.{index_code}"
        period_map = {"daily": "101", "weekly": "102", "monthly": "103"}
        klt = period_map.get(period, "101")

        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "ut": "7eea3edcaed734bea9cbfce24459ed57",
            "klt": klt,
            "fqt": "0",
            "secid": secid,
            "beg": "20200101",
            "end": datetime.now().strftime("%Y%m%d"),
            "lmt": "10000",
            "_": str(int(datetime.now().timestamp() * 1000)),
        }

        url = f"{self._KLINE_URL}/api/qt/stock/kline/get"
        data = await self._fetch_json(url, params)
        if not data or "data" not in data or data["data"] is None:
            return []

        klines = data["data"].get("klines", [])
        result = []
        for line in klines:
            parts = line.split(",")
            if len(parts) < 7:
                continue
            result.append({
                "date": parts[0],
                "open": float(parts[1]),
                "close": float(parts[2]),
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": float(parts[5]),
                "amount": float(parts[6]),
            })
        return result

    async def refresh_stock_list(self, db) -> None:
        from sqlalchemy import select
        from backend.app.models.stock import Stock

        params = {
            "pn": "1",
            "pz": "6000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f12",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f12,f14",
            "_": str(int(datetime.now().timestamp() * 1000)),
        }
        url = f"{self._BASE_URL}/api/qt/clist/get"
        data = await self._fetch_json(url, params)
        if not data or "data" not in data or data["data"] is None:
            return

        diffs = data["data"].get("diff", [])
        for r in diffs:
            code = str(r.get("f12", ""))
            name = str(r.get("f14", ""))
            existing = await db.execute(
                select(Stock).where(Stock.code == code)
            )
            if not existing.scalars().first():
                db.add(Stock(code=code, name=name))
        await db.commit()

    async def health_check(self) -> bool:
        if not await super().health_check():
            return False
        try:
            await self._fetch_json(
                f"{self._BASE_URL}/api/qt/clist/get",
                {
                    "pn": "1", "pz": "1", "po": "1", "np": "1",
                    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                    "fltt": "2", "invt": "2",
                    "fid": "f3", "fs": "m:1+t:2",
                    "fields": "f12",
                    "_": str(int(datetime.now().timestamp() * 1000)),
                },
            )
            return True
        except Exception:
            return False

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
