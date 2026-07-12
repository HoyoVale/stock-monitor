from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.stock import StockResponse
from app.services.stock_service import stock_service

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("")
async def list_stocks(search: Optional[str] = "", db: AsyncSession = Depends(get_db)):
    if search:
        stocks = await stock_service.search_stocks(db, search)
    else:
        stocks = await stock_service.get_all_stocks(db)
    if not stocks:
        await stock_service.refresh_stock_list(db)
        stocks = await stock_service.get_all_stocks(db)
    return [StockResponse.model_validate(s) for s in stocks]


@router.get("/{code}/quotes")
async def get_stock_quote(code: str):
    quotes = await stock_service.get_realtime_quotes(codes=[code])
    if quotes:
        return quotes[0]
    return {"code": code, "name": "", "price": 0, "change": 0, "change_pct": 0,
            "open": 0, "high": 0, "low": 0, "volume": 0, "amount": 0}


@router.get("/{code}/bars")
async def get_stock_bars(
    code: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    return await stock_service.get_daily_bars(code, start, end)
