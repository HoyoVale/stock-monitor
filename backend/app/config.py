import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./stock_monitor.db")
AKSHARE_ENABLE: bool = os.getenv("AKSHARE_ENABLE", "true").lower() == "true"
TRADING_ONLY: bool = os.getenv("TRADING_ONLY", "true").lower() == "true"
REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", "300"))
TRADING_START_MORNING: str = "09:30"
TRADING_END_MORNING: str = "11:30"
TRADING_START_AFTERNOON: str = "13:00"
TRADING_END_AFTERNOON: str = "15:00"

# 数据源配置
DATA_SOURCE: str = os.getenv("DATA_SOURCE", "akshare")
BACKUP_DATA_SOURCE: str = os.getenv("BACKUP_DATA_SOURCE", "eastmoney")
DS_FAILURE_THRESHOLD: int = int(os.getenv("DS_FAILURE_THRESHOLD", "3"))

INDEX_CODES: dict[str, str] = {
    "shanghai": "000001",
    "shenzhen": "399001",
    "chi_next": "399006",
    "kcb": "000688",
}

# 通知配置
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM: str = os.getenv("SMTP_FROM", SMTP_USER)
ALERT_EMAIL_TO: str = os.getenv("ALERT_EMAIL_TO", "")
WECHAT_WEBHOOK_URL: str = os.getenv("WECHAT_WEBHOOK_URL", "")
DINGTALK_WEBHOOK_URL: str = os.getenv("DINGTALK_WEBHOOK_URL", "")
