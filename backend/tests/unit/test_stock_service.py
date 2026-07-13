import pytest
from unittest.mock import AsyncMock, patch

from app.services.stock_service import StockService


@pytest.mark.asyncio
async def test_stock_service_init():
    service = StockService()
    assert service._quote_cache == {}
    assert service._cache_time is None
    assert service._datasource is None


@pytest.mark.asyncio
async def test_get_realtime_quotes_delegates_to_datasource():
    service = StockService()
    
    mock_ds = AsyncMock()
    mock_ds._try_with_fallback = AsyncMock(return_value=[
        {"code": "000001", "name": "平安银行", "price": 10.0}
    ])
    service._datasource = mock_ds

    result = await service.get_realtime_quotes()
    assert len(result) == 1
    assert result[0]["code"] == "000001"


@pytest.mark.asyncio
async def test_get_daily_bars_uses_db_then_fallback():
    service = StockService()
    
    mock_ds = AsyncMock()
    mock_ds._try_with_fallback = AsyncMock(return_value=[
        {"date": "2026-01-01", "open": 10.0, "high": 11.0, "low": 9.5, "close": 10.5, "volume": 100000, "amount": 1000000}
    ])
    service._datasource = mock_ds

    result = await service.get_daily_bars("000001")
    assert len(result) == 1
    assert result[0]["close"] == 10.5


@pytest.mark.asyncio
async def test_get_index_bars_delegates_to_datasource():
    service = StockService()
    
    mock_ds = AsyncMock()
    mock_ds._try_with_fallback = AsyncMock(return_value=[
        {"date": "2026-01-01", "open": 3000.0, "high": 3100.0, "low": 2950.0, "close": 3050.0, "volume": 1000000}
    ])
    service._datasource = mock_ds

    result = await service.get_index_bars("000001")
    assert len(result) == 1
    assert result[0]["close"] == 3050.0


@pytest.mark.asyncio
async def test_datasource_health():
    service = StockService()
    
    mock_ds = AsyncMock()
    mock_ds.name = "akshare"
    mock_ds._failure_count = 0
    mock_ds.health_check = AsyncMock(return_value=True)
    mock_ds._backup = AsyncMock()
    mock_ds._backup.name = "eastmoney"
    mock_ds._backup._failure_count = 0
    mock_ds._backup.health_check = AsyncMock(return_value=True)
    service._datasource = mock_ds

    health = await service.datasource_health()
    assert health["primary"]["name"] == "akshare"
    assert health["primary"]["available"] is True
    assert health["backup"]["name"] == "eastmoney"
    assert health["backup"]["available"] is True
