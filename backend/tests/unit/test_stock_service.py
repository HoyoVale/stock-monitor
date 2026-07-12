import pytest
from app.services.stock_service import StockService


@pytest.mark.asyncio
async def test_stock_service_init():
    service = StockService()
    assert service._quote_cache == {}
    assert service._cache_time is None


@pytest.mark.asyncio
async def test_get_realtime_quotes_empty_when_disabled(monkeypatch):
    monkeypatch.setattr("app.services.stock_service.AKSHARE_ENABLE", False)
    service = StockService()
    result = await service.get_realtime_quotes()
    assert result == []


@pytest.mark.asyncio
async def test_get_index_bars_empty_when_disabled(monkeypatch):
    monkeypatch.setattr("app.services.stock_service.AKSHARE_ENABLE", False)
    service = StockService()
    result = await service.get_index_bars("000001")
    assert result == []
