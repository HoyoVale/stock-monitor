from abc import ABC, abstractmethod
from typing import Optional


class BaseDataSource(ABC):
    """Abstract base class for stock market data sources.

    All data source implementations must extend this class and implement
    all abstract methods. The base class provides fallback support.
    """

    name: str = "base"
    _backup: Optional["BaseDataSource"] = None
    _available: bool = True
    _failure_count: int = 0
    _max_failures: int = 3

    @abstractmethod
    async def get_realtime_quotes(self, codes: Optional[list[str]] = None) -> list[dict]:
        """Get real-time quotes for A-share stocks.

        Args:
            codes: Optional list of stock codes to filter. If None, returns all.

        Returns:
            List of dicts with keys: code, name, price, change, change_pct,
            open, high, low, volume, amount.
        """
        ...

    @abstractmethod
    async def get_daily_bars(
        self, code: str, start: Optional[str] = None, end: Optional[str] = None, period: str = "daily"
    ) -> list[dict]:
        """Get daily OHLCV bars for a specific stock.

        Args:
            code: Stock code (e.g. "000001").
            start: Start date string (YYYYMMDD).
            end: End date string (YYYYMMDD).
            period: Bar period (daily, weekly, monthly).

        Returns:
            List of dicts with keys: date, open, high, low, close, volume, amount.
        """
        ...

    @abstractmethod
    async def get_index_bars(self, index_code: str, period: str = "daily") -> list[dict]:
        """Get index daily bars.

        Args:
            index_code: Index code (e.g. "000001" for 上证).
            period: Bar period.

        Returns:
            List of dicts with keys: date, open, high, low, close, volume.
        """
        ...

    @abstractmethod
    async def refresh_stock_list(self, db) -> None:
        """Refresh the stock list from the data source into the database.

        Args:
            db: SQLAlchemy AsyncSession.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the data source is currently available."""
        return self._available and self._failure_count < self._max_failures

    async def _mark_failure(self) -> None:
        """Record a failure and potentially mark source as unavailable."""
        self._failure_count += 1
        if self._failure_count >= self._max_failures:
            self._available = False

    async def _mark_success(self) -> None:
        """Reset failure count on success."""
        self._failure_count = 0
        self._available = True

    async def _try_with_fallback(self, method_name: str, *args, **kwargs):
        """Attempt a method call; fall back to backup source on failure.

        Args:
            method_name: Name of the method to call.
            *args, **kwargs: Arguments to pass to the method.

        Returns:
            Result from primary or backup source.

        Raises:
            RuntimeError: If both primary and backup sources fail.
        """
        method = getattr(self, method_name, None)
        if method is None:
            raise AttributeError(f"Method {method_name} not found on {self.name}")

        try:
            result = await method(*args, **kwargs)
            await self._mark_success()
            return result
        except Exception as e:
            await self._mark_failure()
            if self._backup and self._backup is not self:
                if await self._backup.health_check():
                    try:
                        backup_method = getattr(self._backup, method_name)
                        result = await backup_method(*args, **kwargs)
                        return result
                    except Exception as backup_e:
                        raise RuntimeError(
                            f"Both primary ({self.name}) and backup ({self._backup.name}) "
                            f"sources failed for {method_name}: {e}, {backup_e}"
                        ) from backup_e
            raise
