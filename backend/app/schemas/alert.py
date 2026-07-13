from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertRuleCreate(BaseModel):
    stock_code: str
    alert_type: str
    threshold: float
    enabled: bool = True


class AlertRuleResponse(BaseModel):
    id: int
    stock_code: str
    alert_type: str
    threshold: float
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertRecordResponse(BaseModel):
    id: int
    rule_id: Optional[int] = None
    stock_code: str
    triggered_at: datetime
    price: Optional[float] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True
