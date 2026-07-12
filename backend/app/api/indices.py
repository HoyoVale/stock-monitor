from typing import Optional

from fastapi import APIRouter

from app.config import INDEX_CODES
from app.services.stock_service import stock_service

router = APIRouter(prefix="/api/indices", tags=["indices"])

INDEX_NAMES = {
    "000001": "上证指数",
    "399001": "深证成指",
    "399006": "创业板指",
    "000688": "科创50",
}


@router.get("")
async def get_indices():
    quotes = await stock_service.get_index_quotes()
    if not quotes:
        return [
            {"code": k, "name": v, "price": 0, "change": 0, "change_pct": 0}
            for k, v in INDEX_NAMES.items()
        ]
    return [
        {
            "code": q["code"],
            "name": INDEX_NAMES.get(q["code"], q["name"]),
            "price": q["price"],
            "change": q["change"],
            "change_pct": q["change_pct"],
        }
        for q in quotes
    ]


@router.get("/{code}/bars")
async def get_index_bars(code: str, period: Optional[str] = "1y"):
    bars = await stock_service.get_index_bars(code)
    now = len(bars)
    period_map = {"1m": 20, "3m": 60, "6m": 120, "1y": 250}
    limit = period_map.get(period, 250)
    return bars[-limit:] if now > limit else bars
