from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey

from app.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    stock_code = Column(String(10), nullable=False)
    alert_type = Column(String(32), nullable=False)
    threshold = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class AlertRecord(Base):
    __tablename__ = "alert_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    rule_id = Column(Integer, nullable=True)
    stock_code = Column(String(10), nullable=False)
    triggered_at = Column(DateTime, default=datetime.now)
    price = Column(Float, nullable=True)
    message = Column(String(256), nullable=True)
