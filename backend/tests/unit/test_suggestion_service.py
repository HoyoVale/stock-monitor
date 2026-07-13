import pytest
from unittest.mock import patch, AsyncMock

from app.services.suggestion_service import SuggestionService, RATING_THRESHOLDS, SIGNAL_TO_WEIGHT


def test_signal_to_weight_maps_correctly():
    assert SIGNAL_TO_WEIGHT["golden_cross"] == 1.0
    assert SIGNAL_TO_WEIGHT["dead_cross"] == 0.0
    assert SIGNAL_TO_WEIGHT["neutral"] == 0.5


def test_rating_thresholds():
    thresholds = sorted(RATING_THRESHOLDS, key=lambda t: t[0], reverse=True)
    for t, _, _, _ in thresholds:
        assert 0 <= t <= 100


@pytest.mark.asyncio
async def test_analyze_empty_result():
    svc = SuggestionService()
    with patch.object(svc.indicator_service, "calc_all_indicators", new_callable=AsyncMock) as mock_calc:
        mock_calc.return_value = []
        result = await svc.analyze("600519", "贵州茅台")
    assert result["stock_code"] == "600519"
    assert result["overall_score"] == 0
    assert result["rating_label"] == "暂无数据"


@pytest.mark.asyncio
async def test_analyze_buy_signal():
    svc = SuggestionService()
    buy_indicators = [
        {"name": "MACD", "signal": "golden_cross", "values": {"dif": 1.0, "dea": 0.5, "hist": 0.5}},
        {"name": "RSI", "signal": "oversold", "values": {"value": 28.0}},
        {"name": "KDJ", "signal": "golden_cross", "values": {"k": 40.0, "d": 30.0, "j": 60.0}},
        {"name": "BOLL", "signal": "price_below_lower", "values": {"upper": 20.0, "middle": 15.0, "lower": 10.0}},
        {"name": "MA_ARRANGE", "signal": "bullish", "values": {"ma5": 15.0, "ma10": 14.0, "ma20": 13.0, "ma60": 12.0}},
    ]
    with patch.object(svc.indicator_service, "calc_all_indicators", new_callable=AsyncMock) as mock_calc:
        mock_calc.return_value = buy_indicators
        result = await svc.analyze("000001", "平安银行")
    assert result["overall_score"] >= 80
    assert result["indicators"]
    assert result["data_source"]
    assert "risk_tips" in result
    assert "position_suggestion" in result
