"""Tests for the multi-datasource abstraction layer."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.services.datasource.base import BaseDataSource
from backend.app.services.datasource.akshare_source import AkshareDataSource
from backend.app.services.datasource.eastmoney_source import EastmoneyDataSource


class TestBaseDataSource:
    """Test the abstract base class and fallback mechanism."""

    def test_base_is_abstract(self):
        """BaseDataSource should not be directly instantiable."""
        with pytest.raises(TypeError):
            BaseDataSource()

    def test_mark_failure_and_recovery(self):
        """Test failure counting and recovery."""
        # Use a concrete subclass for testing
        source = AkshareDataSource()
        source._max_failures = 2

        assert source._failure_count == 0

        source._mark_failure()
        assert source._failure_count == 1
        assert source._available is True

        source._mark_failure()
        assert source._failure_count == 2
        assert source._available is False

        source._mark_success()
        assert source._failure_count == 0
        assert source._available is True

    @pytest.mark.asyncio
    async def test_fallback_to_backup_on_failure(self):
        """Test that a primary source failure triggers fallback."""
        primary = AkshareDataSource()
        backup = EastmoneyDataSource()

        # Make primary always fail
        async def mock_fail(*args, **kwargs):
            raise RuntimeError("Primary down")
        primary.get_realtime_quotes = mock_fail

        # Make backup return data
        async def mock_backup(*args, **kwargs):
            return [{"code": "000001", "name": "平安银行", "price": 10.0}]
        backup.get_realtime_quotes = mock_backup
        backup.health_check = AsyncMock(return_value=True)

        primary._backup = backup

        result = await primary._try_with_fallback("get_realtime_quotes")
        assert len(result) == 1
        assert result[0]["code"] == "000001"

    @pytest.mark.asyncio
    async def test_fallback_both_fail(self):
        """Test that RuntimeError is raised when both sources fail."""
        primary = AkshareDataSource()
        backup = EastmoneyDataSource()

        async def mock_fail(*args, **kwargs):
            raise RuntimeError("Primary down")
        primary.get_realtime_quotes = mock_fail

        async def mock_backup_fail(*args, **kwargs):
            raise RuntimeError("Backup down")
        backup.get_realtime_quotes = mock_backup_fail
        backup.health_check = AsyncMock(return_value=True)

        primary._backup = backup

        with pytest.raises(RuntimeError, match="Both primary.*backup.*sources failed"):
            await primary._try_with_fallback("get_realtime_quotes")


class TestAkshareDataSource:
    """Test the Akshare data source implementation."""

    def test_name(self):
        source = AkshareDataSource()
        assert source.name == "akshare"

    def test_health_check_no_akshare(self):
        """Health check returns False when akshare is disabled."""
        with patch("backend.app.services.datasource.akshare_source.AKSHARE_ENABLE", False):
            source = AkshareDataSource()
            result = asyncio.run_coroutine(source.health_check())
            assert result is False

    def test_default_values(self):
        source = AkshareDataSource()
        assert source._available is True
        assert source._failure_count == 0
        assert source._backup is None


class TestEastmoneyDataSource:
    """Test the Eastmoney data source implementation."""

    def test_name(self):
        source = EastmoneyDataSource()
        assert source.name == "eastmoney"

    def test_default_values(self):
        source = EastmoneyDataSource()
        assert source._available is True
        assert source._failure_count == 0

    def test_timeout_configurable(self):
        source = EastmoneyDataSource(timeout=30.0)
        assert source._timeout == 30.0

    @pytest.mark.asyncio
    async def test_resolve_market_shanghai(self):
        source = EastmoneyDataSource()
        assert await source._resolve_market("600000") == "1"
        assert await source._resolve_market("000001") == "0"
        assert await source._resolve_market("300750") == "0"

    @pytest.mark.asyncio
    async def test_parse_kline_response(self):
        source = EastmoneyDataSource()
        # Test with valid kline data parsing
        mock_resp = {
            "data": {
                "klines": [
                    "2026-01-01,10.0,10.5,11.0,9.8,1000000,10500000",
                    "2026-01-02,10.5,10.8,11.2,10.3,1200000,12600000",
                ]
            }
        }

        with patch.object(source, "_fetch_json", AsyncMock(return_value=mock_resp)):
            bars = await source.get_daily_bars("000001", start="20260101", end="20260102")
            assert len(bars) == 2
            assert bars[0]["open"] == 10.0
            assert bars[0]["close"] == 10.5
            assert bars[1]["open"] == 10.5

    @pytest.mark.asyncio
    async def test_empty_response(self):
        source = EastmoneyDataSource()
        with patch.object(source, "_fetch_json", AsyncMock(return_value={"data": None})):
            bars = await source.get_daily_bars("000001")
            assert bars == []

    @pytest.mark.asyncio
    async def test_close_client(self):
        source = EastmoneyDataSource()
        source._client = AsyncMock()
        await source.close()
        assert source._client is None


import asyncio
