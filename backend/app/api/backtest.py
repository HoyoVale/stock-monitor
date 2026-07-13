"""回测 API。"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.backtest import BacktestResult
from app.services.backtest_service import backtest_service

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    threshold: float = 60.0


class BacktestResponse(BaseModel):
    id: int
    stock_code: str
    start_date: str
    end_date: str
    total_return: Optional[float] = None
    win_rate: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    trade_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("")
async def run_backtest(
    req: BacktestRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """执行历史回测并持久化结果。"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except ValueError:
        raise HTTPException(400, "日期格式错误，应为 YYYY-MM-DD")

    if start >= end:
        raise HTTPException(400, "开始日期必须早于结束日期")

    if req.threshold < 0 or req.threshold > 100:
        raise HTTPException(400, "threshold 必须在 0-100 之间")

    result = await backtest_service.run(
        code=req.stock_code,
        start=req.start_date,
        end=req.end_date,
        threshold=req.threshold,
    )

    if "error" in result:
        raise HTTPException(400, result["error"])

    # Persist result for the current user
    bt = BacktestResult(
        user_id=user.id if user else None,
        stock_code=req.stock_code,
        start_date=req.start_date,
        end_date=req.end_date,
        total_return=result.get("total_return"),
        win_rate=result.get("win_rate"),
        max_drawdown=result.get("max_drawdown"),
        sharpe_ratio=result.get("sharpe_ratio"),
        trade_count=result.get("trade_count", 0),
    )
    db.add(bt)
    await db.commit()
    await db.refresh(bt)

    result["id"] = bt.id
    return result


@router.get("/history", response_model=list[BacktestResponse])
async def list_backtest_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """列出当前用户的回测历史。"""
    stmt = select(BacktestResult).order_by(BacktestResult.created_at.desc()).limit(limit)
    if user:
        stmt = stmt.where(BacktestResult.user_id == user.id)
    else:
        stmt = stmt.where(BacktestResult.user_id.is_(None))
    result = await db.execute(stmt)
    return [BacktestResponse.model_validate(r) for r in result.scalars().all()]


@router.delete("/history/{result_id}")
async def delete_backtest_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """删除一条回测历史记录。"""
    from sqlalchemy import delete as sa_delete
    stmt = sa_delete(BacktestResult).where(BacktestResult.id == result_id)
    if user:
        stmt = stmt.where(BacktestResult.user_id == user.id)
    await db.execute(stmt)
    await db.commit()
    return {"ok": True}
