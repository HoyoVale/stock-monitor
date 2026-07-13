"""
股价预测服务 — 基于 sklearn LinearRegression + 特征工程的轻量预测。

使用 async + ProcessPoolExecutor 避免阻塞主线程。
内置模型缓存: 当日线数据未变更时复用已训练模型。
输出: 未来 N 日预测价格 + 置信区间 + 准确率指标。
"""

import asyncio
import hashlib
import logging
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


def _make_data_hash(closes: List[float]) -> str:
    """计算收盘价序列的哈希，用于缓存键。"""
    raw = ",".join(f"{c:.4f}" for c in closes[-30:])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _train_and_predict(
    closes: List[float],
    volumes: List[float],
    highs: List[float],
    lows: List[float],
    days: int,
    lookback: int = 20,
) -> Dict[str, Any]:
    """在进程池中执行 sklearn 训练+预测，避免阻塞事件循环。

    Args:
        closes: 历史收盘价序列
        volumes: 历史成交量序列
        highs: 历史最高价序列
        lows: 历史最低价序列
        days: 预测天数
        lookback: 滑动窗口大小

    Returns:
        包含预测结果、准确率指标的字典
    """
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    def _make_features(idx: int, seq_len: int) -> np.ndarray:
        """从时序位置构造特征向量。"""
        c = closes[max(0, idx - lookback) : idx + 1]
        v = volumes[max(0, idx - lookback) : idx + 1]
        h = highs[max(0, idx - lookback) : idx + 1]
        l = lows[max(0, idx - lookback) : idx + 1]
        features = []
        # 最近收盘价
        features.append(c[-1])
        # 价格变化率
        if len(c) >= 2:
            features.append((c[-1] - c[-2]) / max(c[-2], 0.01))
        else:
            features.append(0.0)
        # 移动平均 (5 / 10 / 20)
        for w in (5, 10, 20):
            if len(c) >= w:
                features.append(np.mean(c[-w:]))
            else:
                features.append(np.mean(c))
        # 波动率
        if len(c) >= 5:
            features.append(np.std(c[-5:]) / max(np.mean(c[-5:]), 0.01))
        else:
            features.append(0.0)
        # 量价关系
        if len(c) >= 2 and len(v) >= 2:
            features.append(v[-1] / max(np.mean(v[-min(10, len(v)):]), 1.0))
        else:
            features.append(1.0)
        # 当日振幅
        if idx < len(h) and idx < len(l):
            features.append((h[idx] - l[idx]) / max(c[-1], 0.01))
        else:
            features.append(0.0)
        return np.array(features, dtype=np.float64)

    n = len(closes)
    if n < lookback + 5:
        return {"error": f"数据不足，需要至少 {lookback + 5} 个交易日，当前仅 {n} 个"}

    # 构造训练集
    X_list, y_list = [], []
    for i in range(lookback, n - 1):
        feats = _make_features(i, n)
        target = closes[i + 1]  # 预测下一日
        X_list.append(feats)
        y_list.append(target)

    X = np.array(X_list, dtype=np.float64)
    y = np.array(y_list, dtype=np.float64)

    if len(X) < 10:
        return {"error": "训练样本不足"}

    # 归一化
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    X_scaled = scaler_x.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

    # 训练 Ridge 回归
    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y_scaled)

    # 训练集评估
    y_pred_train = model.predict(X_scaled)
    y_pred_real = scaler_y.inverse_transform(y_pred_train.reshape(-1, 1)).ravel()
    mse = np.mean((y - y_pred_real) ** 2)
    mae = np.mean(np.abs(y - y_pred_real))
    mape = np.mean(np.abs((y - y_pred_real) / np.maximum(np.abs(y), 0.01))) * 100

    # 回测准确率: 方向正确率
    pred_diffs = np.diff(y_pred_real)
    real_diffs = np.diff(y)
    direction_correct = np.sum(np.sign(pred_diffs) == np.sign(real_diffs))
    direction_accuracy = direction_correct / max(len(pred_diffs), 1) * 100

    # 递归预测未来 N 日
    last_idx = n - 1
    predictions = []
    current_close = closes[-1]
    # 模拟序列: 用于滚动构造特征
    sim_closes = list(closes)
    sim_volumes = list(volumes)
    sim_highs = list(highs)
    sim_lows = list(lows)

    for day in range(days):
        idx = len(sim_closes) - 1
        feats = _make_features(idx, len(sim_closes))
        feats_scaled = scaler_x.transform(feats.reshape(1, -1))
        pred_scaled = model.predict(feats_scaled)[0]
        pred_price = float(scaler_y.inverse_transform([[pred_scaled]])[0][0])
        # 约束: 价格变动在 ±10% 内
        pred_price = max(current_close * 0.9, min(current_close * 1.1, pred_price))
        predictions.append(pred_price)
        # 滚动更新模拟序列
        sim_closes.append(pred_price)
        sim_volumes.append(volumes[-1])
        sim_highs.append(pred_price * 1.01)
        sim_lows.append(pred_price * 0.99)
        current_close = pred_price

    # 置信区间: ±2 * RMSE
    rmse = np.sqrt(mse)
    lower_bounds = [max(p - 2 * rmse, p * 0.85) for p in predictions]
    upper_bounds = [min(p + 2 * rmse, p * 1.15) for p in predictions]

    # 生成未来日期
    import datetime as dt

    today = dt.date.today()
    future_dates: List[str] = []
    d = today + dt.timedelta(days=1)
    while len(future_dates) < days:
        if d.weekday() < 5:  # 跳过周末
            future_dates.append(d.isoformat())
        d += dt.timedelta(days=1)

    return {
        "predictions": [
            {
                "date": future_dates[i],
                "price": round(predictions[i], 2),
                "lower": round(lower_bounds[i], 2),
                "upper": round(upper_bounds[i], 2),
            }
            for i in range(days)
        ],
        "metrics": {
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "mape_pct": round(mape, 2),
            "direction_accuracy_pct": round(direction_accuracy, 2),
            "training_samples": len(X),
        },
        "last_price": round(closes[-1], 2),
        "trend": "上涨" if predictions[-1] > closes[-1] else "下跌",
    }


class PredictionService:
    """股价预测服务 (单例)。

    内置模型缓存: 以收盘价序列哈希作为缓存键，当日线数据未变更时
    复用已训练模型，避免重复训练。
    """

    def __init__(self) -> None:
        self._executor = ProcessPoolExecutor(max_workers=1)
        # 模型缓存: {stock_code: {"hash": str, "result": dict}}
        self._model_cache: Dict[str, Dict[str, Any]] = {}

    def _get_cached(self, code: str, data_hash: str) -> Optional[Dict[str, Any]]:
        """检查缓存是否命中。

        Args:
            code: 股票代码
            data_hash: 收盘价序列哈希

        Returns:
            缓存结果或 None
        """
        entry = self._model_cache.get(code)
        if entry and entry.get("hash") == data_hash:
            logger.info("模型缓存命中: %s (hash=%s)", code, data_hash)
            return entry["result"]
        return None

    def _set_cache(self, code: str, data_hash: str, result: Dict[str, Any]) -> None:
        """写入缓存。

        Args:
            code: 股票代码
            data_hash: 收盘价序列哈希
            result: 预测结果
        """
        self._model_cache[code] = {"hash": data_hash, "result": result.copy()}
        logger.info("模型缓存写入: %s (hash=%s)", code, data_hash)

    def invalidate_cache(self, code: Optional[str] = None) -> None:
        """清除指定股票或全部缓存。

        Args:
            code: 股票代码，为 None 时清除全部缓存
        """
        if code:
            self._model_cache.pop(code, None)
            logger.info("模型缓存清除: %s", code)
        else:
            self._model_cache.clear()
            logger.info("模型缓存全部清除")

    async def predict(
        self,
        code: str,
        closes: List[float],
        volumes: List[float],
        highs: List[float],
        lows: List[float],
        days: int = 7,
    ) -> Dict[str, Any]:
        """异步预测未来 N 日价格。

        内置模型缓存: 若收盘价序列未变更则复用已训练模型。

        Args:
            code: 股票代码
            closes: 历史收盘价
            volumes: 历史成交量
            highs: 历史最高价
            lows: 历史最低价
            days: 预测天数 (1-30)
        """
        if days < 1 or days > 30:
            return {"error": "预测天数必须在 1-30 之间"}

        if len(closes) < 30:
            return {"error": "历史数据不足，需要至少 30 个交易日"}

        # 检查模型缓存
        data_hash = _make_data_hash(closes)
        cached = self._get_cached(code, data_hash)
        if cached is not None:
            cached_result = cached.copy()
            cached_result["cache_hit"] = True
            return cached_result

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                _train_and_predict,
                closes,
                volumes,
                highs,
                lows,
                days,
            )
            result["stock_code"] = code
            result["cache_hit"] = False
            # 写入缓存
            self._set_cache(code, data_hash, result)
            return result
        except Exception as e:
            logger.exception("预测失败: %s", e)
            return {"error": f"预测失败: {e}"}

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)


prediction_service = PredictionService()
