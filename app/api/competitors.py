from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.services.analysis_service import AnalysisService
from app.schemas.competitor import CompetitorSchema, CompetitorDetailSchema, LicenseSchema, MonthlyTrend, YearlySummarySchema

router = APIRouter()
_analysis = AnalysisService()


@router.get("/competitors", response_model=list[CompetitorSchema])
async def list_competitors(db: AsyncSession = Depends(get_db)):
    """4개사 목록 + 총 품목 수."""
    result = await db.execute(select(Competitor).order_by(Competitor.id))
    competitors = result.scalars().all()

    out = []
    for comp in competitors:
        cnt_result = await db.execute(
            select(func.count(ProductRegistration.id)).where(
                ProductRegistration.competitor_id == comp.id
            )
        )
        total = cnt_result.scalar() or 0
        out.append(
            CompetitorSchema(
                id=comp.id,
                name=comp.name,
                name_short=comp.name_short,
                total_registrations=total,
                created_at=comp.created_at,
                updated_at=comp.updated_at,
            )
        )
    return out


@router.get("/competitors/{competitor_id}", response_model=CompetitorDetailSchema)
async def get_competitor(competitor_id: int, db: AsyncSession = Depends(get_db)):
    """경쟁사 상세 + 최근 12개월 월별 신고 추이 + 전체 라이선스 목록."""
    result = await db.execute(
        select(Competitor)
        .where(Competitor.id == competitor_id)
        .options(selectinload(Competitor.licenses))
    )
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    cnt_result = await db.execute(
        select(func.count(ProductRegistration.id)).where(
            ProductRegistration.competitor_id == competitor_id
        )
    )
    total = cnt_result.scalar() or 0

    trend_data = await _analysis.get_monthly_trend(db, competitor_id, months=12)

    licenses = [LicenseSchema.model_validate(lic) for lic in comp.licenses]
    monthly_trend = [MonthlyTrend(**t) for t in trend_data]

    return CompetitorDetailSchema(
        id=comp.id,
        name=comp.name,
        name_short=comp.name_short,
        total_registrations=total,
        licenses=licenses,
        monthly_trend=monthly_trend,
        created_at=comp.created_at,
        updated_at=comp.updated_at,
    )


@router.get("/competitors/{competitor_id}/yearly", response_model=list[YearlySummarySchema])
async def get_competitor_yearly(competitor_id: int, db: AsyncSession = Depends(get_db)):
    """경쟁사의 연도별 신고 건수 요약."""
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    rows = await db.execute(
        select(
            func.extract("year", func.to_date(ProductRegistration.report_date, "YYYYMMDD")).label("year"),
            func.count(ProductRegistration.id).label("count"),
        )
        .where(
            ProductRegistration.competitor_id == competitor_id,
            ProductRegistration.report_date.isnot(None),
        )
        .group_by("year")
        .order_by(func.extract("year", func.to_date(ProductRegistration.report_date, "YYYYMMDD")).desc())
    )
    return [YearlySummarySchema(year=int(row.year), count=row.count) for row in rows.all()]
