"""prediction_service 单元测试。"""

import math

import pytest

from app.services.prediction_service import _train_and_predict


def _make_price_series(
    start: float, trend: float, noise: float, n: int
):
    """生成模拟价格序列。"""
    import random
    random.seed(42)
    prices = []
    for i in range(n):
        price = start + trend * i + random.gauss(0, noise)
        price = max(price, 0.5)
        prices.append(price)
    return prices


class TestTrainAndPredict:
    def test_insufficient_data(self):
        """数据不足应返回 error。"""
        closes = [10.0] * 10
        vols = [1000] * 10
        highs = [10.5] * 10
        lows = [9.5] * 10
        result = _train_and_predict(closes, vols, highs, lows, days=7)
        assert "error" in result

    def test_predict_up_trend(self):
        """上升趋势应预测上涨。"""
        closes = _make_price_series(10.0, 0.05, 0.2, 80)
        vols = [5000 + i * 10 for i in range(80)]
        highs = [c * 1.02 for c in closes]
        lows = [c * 0.98 for c in closes]
        result = _train_and_predict(closes, vols, highs, lows, days=7)
        assert "error" not in result
        assert len(result["predictions"]) == 7
        assert result["predictions"][-1]["price"] > closes[-1]
        assert result["trend"] == "上涨"
        assert "metrics" in result

    def test_predict_down_trend(self):
        """下降趋势应预测下跌。"""
        closes = _make_price_series(20.0, -0.08, 0.3, 80)
        vols = [3000 + i * 5 for i in range(80)]
        highs = [c * 1.01 for c in closes]
        lows = [c * 0.99 for c in closes]
        result = _train_and_predict(closes, vols, highs, lows, days=7)
        assert "error" not in result
        assert len(result["predictions"]) == 7
        assert result["predictions"][-1]["price"] < closes[-1]
        assert result["trend"] == "下跌"

    def test_prediction_has_confidence_interval(self):
        """预测结果应包含置信区间。"""
        closes = _make_price_series(15.0, 0.02, 0.15, 60)
        vols = [2000] * 60
        highs = [c * 1.02 for c in closes]
        lows = [c * 0.98 for c in closes]
        result = _train_and_predict(closes, vols, highs, lows, days=5)
        assert "error" not in result
        for p in result["predictions"]:
            assert p["lower"] < p["price"] < p["upper"]

    def test_metrics_are_reasonable(self):
        """准确率指标应在合理范围。"""
        closes = _make_price_series(12.0, 0.03, 0.1, 70)
        vols = [4000] * 70
        highs = [c * 1.01 for c in closes]
        lows = [c * 0.99 for c in closes]
        result = _train_and_predict(closes, vols, highs, lows, days=5)
        assert "error" not in result
        m = result["metrics"]
        assert m["rmse"] > 0
        assert m["mae"] > 0
        assert 0 <= m["direction_accuracy_pct"] <= 100
