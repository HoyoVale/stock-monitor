from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Integer as IntCol

from app.database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    name = Column(String(64), nullable=False)
    added_at = Column(DateTime, default=datetime.now)
    sort_order = Column(IntCol, default=0)
    group_name = Column(String(32), default="默认")
