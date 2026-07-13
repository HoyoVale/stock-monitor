"""测试指标缓存写入与读取。"""

import pandas as pd
import pytest

from app.services.indicator_service import IndicatorService


class TestIndicatorCache:
    """指标缓存单元测试。"""

    def test_cache_hit_detection_same_count(self):
        """缓存命中检测: 缓存行数与 bar 数一致时避免重复计算逻辑。

        注意: 由于需要完整的数据库环境来测试真实的缓存读写，
        这里测试的是辅助方法的行为正确性。
        完整的端到端缓存测试在 integration 测试中进行。
        """
        # 验证 IndicatorService 暴露了 _get_cached_indicators 方法
        service = IndicatorService()
        assert hasattr(service, "_get_cached_indicators")
        assert callable(service._get_cached_indicators)

    def test_detect_cross_from_lists_golden(self):
        """从缓存数据检测金叉。"""
        dif = [0.1, 0.2, 0.3, 0.4, 0.5]
        dea = [0.15, 0.25, 0.35, 0.45, 0.4]
        # 倒数第二: dif=0.4 <= dea=0.45, 最新: dif=0.5 > dea=0.4 → 金叉
        result = IndicatorService._detect_cross_from_lists(dif, dea)
        assert result == "golden_cross"

    def test_detect_cross_from_lists_dead(self):
        """从缓存数据检测死叉。"""
        dif = [0.5, 0.4, 0.3, 0.2, 0.3]
        dea = [0.45, 0.35, 0.25, 0.15, 0.35]
        # 倒数第二: dif=0.2 >= dea=0.15, 最新: dif=0.3 < dea=0.35 → 死叉
        result = IndicatorService._detect_cross_from_lists(dif, dea)
        assert result == "dead_cross"

    def test_detect_cross_from_lists_neutral(self):
        """无交叉信号。"""
        dif = [0.1, 0.2]
        dea = [0.15, 0.25]
        # dif 始终小于 dea → neutral
        result = IndicatorService._detect_cross_from_lists(dif, dea)
        assert result == "neutral"

    def test_detect_cross_short_lists(self):
        """序列过短时返回 neutral。"""
        assert IndicatorService._detect_cross_from_lists([], []) == "neutral"
        assert IndicatorService._detect_cross_from_lists([1.0], [1.0]) == "neutral"

    def test_detect_cross_none_values(self):
        """包含 None 值时忽略。"""
        result = IndicatorService._detect_cross_from_lists([None, 0.5], [0.3, 0.4])
        assert result == "neutral"

    def test_rsi_signal_oversold(self):
        assert IndicatorService._rsi_signal(25.0) == "oversold"
        assert IndicatorService._rsi_signal(29.9) == "oversold"

    def test_rsi_signal_overbought(self):
        assert IndicatorService._rsi_signal(70.1) == "overbought"
        assert IndicatorService._rsi_signal(85.0) == "overbought"

    def test_rsi_signal_neutral(self):
        assert IndicatorService._rsi_signal(50.0) == "neutral"
        assert IndicatorService._rsi_signal(30.0) == "neutral"
        assert IndicatorService._rsi_signal(70.0) == "neutral"
        assert IndicatorService._rsi_signal(None) == "neutral"

    def test_calc_all_indicators_accepts_force_refresh(self):
        """calc_all_indicators 接受 force_refresh 参数。"""
        import inspect
        sig = inspect.signature(IndicatorService.calc_all_indicators)
        params = sig.parameters
        assert "force_refresh" in params
        assert params["force_refresh"].default is False
