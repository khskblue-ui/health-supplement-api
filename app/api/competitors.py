from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.schemas.competitor import CompetitorSchema, CompetitorDetailSchema, MonthlyTrend, YearlySummarySchema

router = APIRouter()


@router.get("/competitors", response_model=list[CompetitorSchema])
async def list_competitors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competitor).order_by(Competitor.id))
    competitors = result.scalars().all()

    out = []
    for comp in competitors:
        cnt = await db.execute(
            select(func.count(ProductRegistration.id)).where(
                ProductRegistration.competitor_id == comp.id
            )
        )
        out.append(CompetitorSchema(
            id=comp.id,
            name=comp.name,
            name_short=comp.name_short,
            total_registrations=cnt.scalar() or 0,
            created_at=comp.created_at,
        ))
    return out


@router.get("/competitors/{competitor_id}", response_model=CompetitorDetailSchema)
async def get_competitor(competitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competitor).where(Competitor.id == competitor_id))
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    total = (await db.execute(
        select(func.count(ProductRegistration.id)).where(
            ProductRegistration.competitor_id == competitor_id
        )
    )).scalar() or 0

    # 최근 12개월 월별 추이 (mod_dt 기준)
    rows = await db.execute(
        select(
            func.substr(ProductRegistration.mod_dt, 1, 6).label("ym"),
            func.count(ProductRegistration.id).label("cnt"),
        )
        .where(
            ProductRegistration.competitor_id == competitor_id,
            ProductRegistration.mod_dt.isnot(None),
        )
        .group_by("ym")
        .order_by("ym")
        .limit(12)
    )
    monthly_trend = [
        MonthlyTrend(year_month=f"{r.ym[:4]}-{r.ym[4:6]}", count=r.cnt)
        for r in rows.all()
    ]

    return CompetitorDetailSchema(
        id=comp.id,
        name=comp.name,
        name_short=comp.name_short,
        total_registrations=total,
        monthly_trend=monthly_trend,
        created_at=comp.created_at,
    )


@router.get("/competitors/{competitor_id}/yearly", response_model=list[YearlySummarySchema])
async def get_competitor_yearly(competitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competitor).where(Competitor.id == competitor_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Competitor not found")

    rows = await db.execute(
        select(
            func.substr(ProductRegistration.mod_dt, 1, 4).label("yr"),
            func.count(ProductRegistration.id).label("cnt"),
        )
        .where(
            ProductRegistration.competitor_id == competitor_id,
            ProductRegistration.mod_dt.isnot(None),
        )
        .group_by("yr")
        .order_by(func.substr(ProductRegistration.mod_dt, 1, 4).desc())
    )
    return [YearlySummarySchema(year=int(r.yr), count=r.cnt) for r in rows.all()]
