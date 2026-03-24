from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.dashboard import DashboardResponse, CompetitorSummary
from app.schemas.registration import RegistrationSchema

router = APIRouter()
_service = AnalysisService()


@router.get("/dashboard/recent", response_model=DashboardResponse)
async def get_recent_dashboard(db: AsyncSession = Depends(get_db)):
    """4개사 최근 30일 신규 신고 현황 요약."""
    data = await _service.get_dashboard_data(db)

    summaries = []
    for item in data["competitors"]:
        summaries.append(
            CompetitorSummary(
                id=item["id"],
                name=item["name"],
                name_short=item["name_short"],
                recent_count=item["recent_count"],
                last_7_days_count=item["last_7_days_count"],
                latest_products=[
                    RegistrationSchema.model_validate(p)
                    for p in item["latest_products"]
                ],
            )
        )

    return DashboardResponse(competitors=summaries, as_of=data["as_of"])
