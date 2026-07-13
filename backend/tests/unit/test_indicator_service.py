import pytest
import pandas as pd
from unittest.mock import patch, AsyncMock

from app.services.indicator_service import IndicatorService


def sample_ohlc():
    import numpy as np
    n = 120
    rng = pd.date_range("2026-01-01", periods=n, freq="B")
    close = 10 + pd.Series(range(n)) * 0.1 + pd.Series(np.random.randn(n) * 0.2)
    df = pd.DataFrame({
        "open": close - 0.1,
        "high": close + 0.3,
        "low": close - 0.3,
        "close": close,
        "volume": 10000 + pd.Series(range(n)) * 10,
    })
    return df


def test_calc_macd():
    df = sample_ohlc()
    svc = IndicatorService()
    result = svc.calc_macd(df)
    assert "dif" in result
    assert "dea" in result
    assert "hist" in result
    assert result["signal"] in ("golden_cross", "dead_cross", "neutral")
    assert isinstance(result["dif"], float)


def test_calc_rsi():
    df = sample_ohlc()
    svc = IndicatorService()
    result = svc.calc_rsi(df, period=14)
    assert "value" in result
    assert result["signal"] in ("oversold", "overbought", "neutral")
    assert 0 <= result["value"] <= 100


def test_calc_kdj():
    df = sample_ohlc()
    svc = IndicatorService()
    result = svc.calc_kdj(df)
    assert "k" in result
    assert "d" in result
    assert "j" in result
    assert result["signal"] in ("golden_cross", "dead_cross", "neutral")


def test_calc_boll():
    df = sample_ohlc()
    svc = IndicatorService()
    result = svc.calc_boll(df)
    assert "upper" in result
    assert "middle" in result
    assert "lower" in result
    assert result["signal"] in ("price_above_upper", "price_below_lower", "price_in_band")


def test_calc_ma_arrange():
    df = sample_ohlc()
    svc = IndicatorService()
    result = svc.calc_ma_arrange(df)
    assert "ma5" in result
    assert "ma10" in result
    assert "ma20" in result
    assert "ma60" in result
    assert result["signal"] in ("bullish", "bearish", "neutral")
