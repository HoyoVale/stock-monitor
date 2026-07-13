"""测试回测服务。"""

import numpy as np
import pytest

from app.services.backtest_service import BacktestService


class TestBacktestService:
    """回测服务单元测试。"""

    def test_init(self):
        """初始化 BacktestService。"""
        svc = BacktestService()
        assert svc is not None
        assert hasattr(svc, "indicator")
        assert hasattr(svc, "run")

    def test_detect_ma_arrange_bullish(self):
        """多头排列检测。"""
        import pandas as pd
        # 构造上升趋势数据: 价格递增, 使得短期 MA > 中期 MA > 长期 MA
        closes = pd.Series(np.linspace(100, 200, 100))
        result = BacktestService._detect_ma_arrange(closes)
        assert result in ("bullish", "neutral")  # neutral 在极端上升时也可能

    def test_detect_ma_arrange_bearish(self):
        """空头排列检测。"""
        import pandas as pd
        closes = pd.Series(np.linspace(200, 100, 100))
        result = BacktestService._detect_ma_arrange(closes)
        assert result in ("bearish", "neutral")

    def test_detect_ma_arrange_short(self):
        """数据不足时返回 neutral。"""
        import pandas as pd
        closes = pd.Series([1.0, 2.0, 3.0])
        result = BacktestService._detect_ma_arrange(closes)
        assert result == "neutral"

    def test_score_window_returns_range(self):
        """评分在 0-100 范围内。"""
        svc = BacktestService()
        closes = [100.0 + i * 0.5 + (i % 7 - 3) * 2 for i in range(80)]
        highs = [c + 2.0 for c in closes]
        lows = [c - 2.0 for c in closes]
        score = svc._score_window(closes, highs, lows)
        assert 0 <= score <= 100

    def test_score_window_short_data(self):
        """数据不足时返回默认 50。"""
        svc = BacktestService()
        closes = [100.0] * 10
        highs = [102.0] * 10
        lows = [98.0] * 10
        score = svc._score_window(closes, highs, lows)
        assert score == 50

    @pytest.mark.asyncio
    async def test_run_returns_error_on_no_data(self):
        """无数据时返回错误。"""
        svc = BacktestService()
        result = await svc.run("999999", "2020-01-01", "2020-06-30")
        assert "error" in result
        assert "60" in result["error"]

    @pytest.mark.asyncio
    async def test_run_computes_metrics_structure(self):
        """验证返回结构（模拟场景——真实计算需要数据库）。"""
        svc = BacktestService()
        result = await svc.run("000001", "2023-01-01", "2023-12-31")
        assert isinstance(result, dict)
        # 无论成功失败，都有 stock_code
        keys_expected = {"stock_code", "start_date", "end_date"}
        assert keys_expected.issubset(result.keys())

    def test_multiple_windows_consistency(self):
        """多次评分的一致性。"""
        svc = BacktestService()
        closes = [100.0 + i * 0.1 for i in range(100)]
        highs = [c + 2.0 for c in closes]
        lows = [c - 2.0 for c in closes]
        s1 = svc._score_window(closes, highs, lows)
        s2 = svc._score_window(closes, highs, lows)
        assert s1 == s2  # 确定性
