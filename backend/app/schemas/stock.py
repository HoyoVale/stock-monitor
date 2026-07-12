from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class StockResponse(BaseModel):
    code: str
    name: str
    exchange: Optional[str] = None
    industry: Optional[str] = None

    class Config:
        from_attributes = True


class QuoteResponse(BaseModel):
    code: str
    name: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    volume: float
    amount: float


class DailyBarResponse(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
    amount: Optional[float] = None


class IndexResponse(BaseModel):
    code: str
    name: str
    price: float
    change: float
    change_pct: float


class WatchlistCreate(BaseModel):
    code: str
    name: str
    group_name: str = "默认"


class WatchlistUpdate(BaseModel):
    sort_order: Optional[int] = None
    group_name: Optional[str] = None


class WatchlistResponse(BaseModel):
    id: int
    code: str
    name: str
    added_at: datetime
    sort_order: int
    group_name: str

    class Config:
        from_attributes = True
