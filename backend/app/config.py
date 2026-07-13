import os

# Version — single source of truth
with open(os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")) as f:
    VERSION = f.read().strip()

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

# CORS — restrict in production
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")

# Security
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
RATE_LIMIT: str = os.getenv("RATE_LIMIT", "60/minute")

# SMTP
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASS: str = os.getenv("SMTP_PASS", "")

# Webhook
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
