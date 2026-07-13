"""预测 API。

POST /api/predictions/{code} — 使用历史 K 线数据预测未来 N 日收盘价。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.prediction_service import prediction_service
from app.services.stock_service import stock_service

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


class PredictionRequest(BaseModel):
    days: int = Field(default=7, ge=1, le=30, description="预测天数 (1-30)")


class PredictionResponse(BaseModel):
    stock_code: str
    last_price: float
    trend: str
    predictions: list
    metrics: dict


@router.post("/{code}")
async def predict_stock(code: str, req: PredictionRequest = PredictionRequest()):
    """预测股票未来 N 日收盘价。

    使用 sklearn Ridge 回归 + 特征工程。
    返回预测价格、置信区间、模型准确率指标。

    Args:
        code: 股票代码 (如 600519)
        days: 预测天数，默认 7，范围 1-30
    """
    # 获取历史 K 线数据
    bars = await stock_service.fetch_history_bars(code, count=120)
    if not bars or len(bars) < 30:
        raise HTTPException(
            400,
            f"历史数据不足，股票 {code} 仅有 {len(bars) if bars else 0} 个交易日数据，需要至少 30",
        )

    closes = [b["close"] for b in bars]
    volumes = [b.get("volume", 0) for b in bars]
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]

    result = await prediction_service.predict(
        code=code,
        closes=closes,
        volumes=volumes,
        highs=highs,
        lows=lows,
        days=req.days,
    )

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result
