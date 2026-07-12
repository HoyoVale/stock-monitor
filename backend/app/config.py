import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./stock_monitor.db")
AKSHARE_ENABLE: bool = os.getenv("AKSHARE_ENABLE", "true").lower() == "true"
TRADING_ONLY: bool = os.getenv("TRADING_ONLY", "true").lower() == "true"
REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", "300"))
TRADING_START_MORNING: str = "09:30"
TRADING_END_MORNING: str = "11:30"
TRADING_START_AFTERNOON: str = "13:00"
TRADING_END_AFTERNOON: str = "15:00"

INDEX_CODES: dict[str, str] = {
    "shanghai": "000001",
    "shenzhen": "399001",
    "chi_next": "399006",
    "kcb": "000688",
}
