from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    code = Column(String(10), nullable=False)
    name = Column(String(64), nullable=False)
    added_at = Column(DateTime, default=datetime.now)
    sort_order = Column(Integer, default=0)
    group_name = Column(String(32), default="默认")
