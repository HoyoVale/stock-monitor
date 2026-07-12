from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/rules")
async def list_alert_rules():
    return []


@router.post("/rules")
async def create_alert_rule():
    raise HTTPException(501, "not implemented yet")


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: int):
    raise HTTPException(501, "not implemented yet")
