from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.dashboard import ProductionAnalysisResponse, ProductionRecordSchema

router = APIRouter()
_analysis = AnalysisService()


@router.get("/analysis/production", response_model=ProductionAnalysisResponse)
async def get_production_analysis(
    year: str = Query(default=str(datetime.now().year - 1), pattern=r"^\d{4}$"),
    competitor_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """I0310 기반 연간 생산량 비교."""
    data = await _analysis.get_production_analysis(db, year, competitor_id)
    return ProductionAnalysisResponse(
        year=data["year"],
        competitor_id=data["competitor_id"],
        records=[ProductionRecordSchema.model_validate(r) for r in data["records"]],
        total=data["total"],
    )
