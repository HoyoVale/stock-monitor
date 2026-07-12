from fastapi import APIRouter
from app.services.indicator_service import IndicatorService
from app.services.suggestion_service import suggestion_service

router = APIRouter(prefix="/api/indicators", tags=["indicators"])
suggestion_router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("/{code}")
async def get_indicators(code: str):
    service = IndicatorService()
    return await service.calc_all_indicators(code)


@suggestion_router.get("/{code}")
async def get_suggestion(code: str, name: str = ""):
    return await suggestion_service.analyze(code, name)
