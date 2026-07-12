from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint

from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    exchange = Column(String(16), nullable=True)
    market_cap = Column(Float, nullable=True)
    industry = Column(String(64), nullable=True)


class DailyBar(Base):
    __tablename__ = "daily_bars"
    __table_args__ = (UniqueConstraint("code", "date", name="uq_code_date"),)

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)


class IndexBar(Base):
    __tablename__ = "index_bars"
    __table_args__ = (UniqueConstraint("index_code", "date", name="uq_index_date"),)

    id = Column(Integer, primary_key=True)
    index_code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
