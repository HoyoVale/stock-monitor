"""prediction_service 单元测试。"""

import math

import pytest

from app.services.prediction_service import _train_and_predict, _make_data_hash, prediction_service


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


class TestMakeDataHash:
    def test_same_data_produces_same_hash(self):
        """相同数据应产生相同哈希。"""
        closes = _make_price_series(10.0, 0.05, 0.2, 40)
        h1 = _make_data_hash(closes)
        h2 = _make_data_hash(closes)
        assert h1 == h2

    def test_different_data_produces_different_hash(self):
        """不同数据应产生不同哈希。"""
        closes1 = _make_price_series(10.0, 0.05, 0.2, 40)
        closes2 = _make_price_series(15.0, -0.03, 0.1, 40)
        h1 = _make_data_hash(closes1)
        h2 = _make_data_hash(closes2)
        assert h1 != h2

    def test_hash_uses_last_30_only(self):
        """哈希仅使用最近 30 个数据点。"""
        closes_long = _make_price_series(10.0, 0.05, 0.2, 60)
        closes_short = closes_long[-30:]
        h_long = _make_data_hash(closes_long)
        h_short = _make_data_hash(closes_short)
        assert h_long == h_short


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


class TestModelCache:
    """模型缓存测试。"""

    @pytest.mark.asyncio
    async def test_cache_hit_on_identical_data(self):
        """相同数据第二次请求应命中缓存。"""
        prediction_service.invalidate_cache()
        closes = _make_price_series(15.0, 0.02, 0.15, 60)
        vols = [2000] * 60
        highs = [c * 1.02 for c in closes]
        lows = [c * 0.98 for c in closes]

        # 第一次: 缓存未命中
        result1 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert "error" not in result1
        assert result1["cache_hit"] is False

        # 第二次: 应命中缓存
        result2 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert "error" not in result2
        assert result2["cache_hit"] is True
        assert result2["stock_code"] == "000001"

    @pytest.mark.asyncio
    async def test_cache_miss_on_different_data(self):
        """不同数据应触发重训练 (缓存未命中)。"""
        prediction_service.invalidate_cache()
        closes1 = _make_price_series(15.0, 0.02, 0.15, 60)
        closes2 = _make_price_series(18.0, -0.01, 0.2, 60)
        vols = [2000] * 60
        highs1 = [c * 1.02 for c in closes1]
        lows1 = [c * 0.98 for c in closes1]
        highs2 = [c * 1.02 for c in closes2]
        lows2 = [c * 0.98 for c in closes2]

        # 第一次
        result1 = await prediction_service.predict(
            code="000001", closes=closes1, volumes=vols, highs=highs1, lows=lows1, days=5
        )
        assert result1["cache_hit"] is False

        # 不同数据: 应未命中
        result2 = await prediction_service.predict(
            code="000001", closes=closes2, volumes=vols, highs=highs2, lows=lows2, days=5
        )
        assert result2["cache_hit"] is False

    @pytest.mark.asyncio
    async def test_cache_isolated_per_stock_code(self):
        """不同股票代码缓存应隔离。"""
        prediction_service.invalidate_cache()
        closes = _make_price_series(15.0, 0.02, 0.15, 60)
        vols = [2000] * 60
        highs = [c * 1.02 for c in closes]
        lows = [c * 0.98 for c in closes]

        r1 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert r1["cache_hit"] is False

        # 不同代码但相同数据: 应各自独立缓存
        r2 = await prediction_service.predict(
            code="600519", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        # 首次请求该代码，不应命中
        assert r2["cache_hit"] is False

        # 再次请求第一个代码: 应命中
        r3 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert r3["cache_hit"] is True

    @pytest.mark.asyncio
    async def test_invalidate_cache(self):
        """清除缓存后应重新训练。"""
        prediction_service.invalidate_cache()
        closes = _make_price_series(15.0, 0.02, 0.15, 60)
        vols = [2000] * 60
        highs = [c * 1.02 for c in closes]
        lows = [c * 0.98 for c in closes]

        r1 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert r1["cache_hit"] is False

        r2 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert r2["cache_hit"] is True

        # 清除缓存
        prediction_service.invalidate_cache("000001")
        r3 = await prediction_service.predict(
            code="000001", closes=closes, volumes=vols, highs=highs, lows=lows, days=5
        )
        assert r3["cache_hit"] is False
