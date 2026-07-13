from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint

from app.database import Base


class IndicatorCache(Base):
    """缓存每只股票每日的技术指标计算结果，加速重复查询。"""

    __tablename__ = "indicator_cache"
    __table_args__ = (UniqueConstraint("stock_code", "date", name="uq_indicator_code_date"),)

    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)

    macd_dif = Column(Float, nullable=True)
    macd_dea = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)

    rsi_14 = Column(Float, nullable=True)

    kdj_k = Column(Float, nullable=True)
    kdj_d = Column(Float, nullable=True)
    kdj_j = Column(Float, nullable=True)

    boll_upper = Column(Float, nullable=True)
    boll_middle = Column(Float, nullable=True)
    boll_lower = Column(Float, nullable=True)

    ma_5 = Column(Float, nullable=True)
    ma_10 = Column(Float, nullable=True)
    ma_20 = Column(Float, nullable=True)
    ma_60 = Column(Float, nullable=True)

    volume_ma_20 = Column(Float, nullable=True)
