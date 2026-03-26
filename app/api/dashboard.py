from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.schemas.dashboard import DashboardResponse, CompetitorSummary
from app.schemas.registration import RegistrationSchema

router = APIRouter()


@router.get("/dashboard/recent", response_model=DashboardResponse)
async def get_recent_dashboard(db: AsyncSession = Depends(get_db)):
    """4개사 최근 30일/7일 신규 등록 현황 (I0320 mod_dt 기준)."""
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    today = now.strftime("%Y%m%d")
    d30 = (now - timedelta(days=30)).strftime("%Y%m%d")
    d7 = (now - timedelta(days=7)).strftime("%Y%m%d")

    result = await db.execute(select(Competitor).order_by(Competitor.id))
    competitors = result.scalars().all()

    summaries = []
    for comp in competitors:
        recent_count = (await db.execute(
            select(func.count(ProductRegistration.id)).where(
                and_(
                    ProductRegistration.competitor_id == comp.id,
                    ProductRegistration.mod_dt >= d30,
                    ProductRegistration.mod_dt <= today,
                )
            )
        )).scalar() or 0

        last_7 = (await db.execute(
            select(func.count(ProductRegistration.id)).where(
                and_(
                    ProductRegistration.competitor_id == comp.id,
                    ProductRegistration.mod_dt >= d7,
                    ProductRegistration.mod_dt <= today,
                )
            )
        )).scalar() or 0

        latest_result = await db.execute(
            select(ProductRegistration)
            .where(ProductRegistration.competitor_id == comp.id)
            .order_by(ProductRegistration.mod_dt.desc(), ProductRegistration.id.desc())
            .limit(5)
        )
        latest = list(latest_result.scalars().all())

        summaries.append(CompetitorSummary(
            id=comp.id,
            name=comp.name,
            name_short=comp.name_short,
            recent_count=recent_count,
            last_7_days_count=last_7,
            latest_products=[RegistrationSchema.model_validate(p) for p in latest],
        ))

    return DashboardResponse(competitors=summaries, as_of=now.isoformat())
