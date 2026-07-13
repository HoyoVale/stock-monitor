"""回测 API。"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.backtest_service import backtest_service

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    threshold: float = 60.0


@router.post("")
async def run_backtest(req: BacktestRequest):
    """执行历史回测。

    Args:
        stock_code: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        threshold: 买入信号评分阈值 (0-100, 默认 60)
    """
    # 校验日期格式
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

    return result
