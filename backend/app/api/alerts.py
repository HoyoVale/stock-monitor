from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, delete as sa_delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import AlertRule, AlertRecord
from app.schemas.alert import AlertRuleCreate, AlertRuleResponse, AlertRecordResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    stock_code: Optional[str] = None,
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AlertRule).order_by(AlertRule.created_at.desc())
    if stock_code:
        stmt = stmt.where(AlertRule.stock_code == stock_code)
    if enabled_only:
        stmt = stmt.where(AlertRule.enabled == True)
    result = await db.execute(stmt)
    return [AlertRuleResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/rules", status_code=201, response_model=AlertRuleResponse)
async def create_alert_rule(data: AlertRuleCreate, db: AsyncSession = Depends(get_db)):
    if data.alert_type not in ("price_above", "price_below"):
        raise HTTPException(400, "alert_type must be 'price_above' or 'price_below'")
    rule = AlertRule(
        stock_code=data.stock_code,
        alert_type=data.alert_type,
        threshold=data.threshold,
        enabled=data.enabled,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return AlertRuleResponse.model_validate(rule)


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "预警规则不存在")
    await db.execute(sa_delete(AlertRule).where(AlertRule.id == rule_id))
    await db.commit()
    return {"ok": True}


@router.patch("/rules/{rule_id}")
async def toggle_alert_rule(rule_id: int, enabled: bool, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "预警规则不存在")
    rule.enabled = enabled
    await db.commit()
    return {"ok": True, "enabled": enabled}


@router.get("/records", response_model=list[AlertRecordResponse])
async def list_alert_records(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AlertRecord).order_by(AlertRecord.triggered_at.desc()).limit(limit)
    )
    return [AlertRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/unread-count")
async def get_unread_count(
    since: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """返回最近 24 小时内触发的新预警记录数（供前端铃铛徽标使用）。"""
    from datetime import datetime, timedelta
    since_dt = datetime.fromisoformat(since) if since else datetime.now() - timedelta(hours=24)
    result = await db.execute(
        select(func.count(AlertRecord.id)).where(AlertRecord.triggered_at >= since_dt)
    )
    count = result.scalar() or 0
    return {"count": count}
