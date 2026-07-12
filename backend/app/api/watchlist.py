from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.watchlist import WatchlistItem
from app.schemas.stock import WatchlistCreate, WatchlistUpdate, WatchlistResponse

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("")
async def list_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WatchlistItem).order_by(WatchlistItem.sort_order, WatchlistItem.added_at)
    )
    items = result.scalars().all()
    return [WatchlistResponse.model_validate(i) for i in items]


@router.post("", status_code=201)
async def add_to_watchlist(data: WatchlistCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(WatchlistItem).where(WatchlistItem.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "该股票已在自选列表中")
    item = WatchlistItem(code=data.code, name=data.name, group_name=data.group_name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return WatchlistResponse.model_validate(item)


@router.delete("/{item_id}")
async def remove_from_watchlist(item_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(sa_delete(WatchlistItem).where(WatchlistItem.id == item_id))
    await db.commit()
    return {"ok": True}


@router.put("/{item_id}")
async def update_watchlist_item(
    item_id: int, data: WatchlistUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WatchlistItem).where(WatchlistItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "自选股不存在")
    if data.sort_order is not None:
        item.sort_order = data.sort_order
    if data.group_name is not None:
        item.group_name = data.group_name
    await db.commit()
    await db.refresh(item)
    return WatchlistResponse.model_validate(item)
