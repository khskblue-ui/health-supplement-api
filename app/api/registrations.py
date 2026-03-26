from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.schemas.registration import RegistrationSchema, RegistrationListResponse

router = APIRouter()


@router.get(
    "/competitors/{competitor_id}/registrations",
    response_model=RegistrationListResponse,
)
async def list_registrations(
    competitor_id: int,
    period: str = Query("monthly", pattern="^(monthly|yearly)$"),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """월별/연도별 이력추적 등록 품목 리스트 (mod_dt 기준)."""
    comp_result = await db.execute(select(Competitor).where(Competitor.id == competitor_id))
    if not comp_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Competitor not found")

    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    conditions = [ProductRegistration.competitor_id == competitor_id]

    if period == "monthly":
        year = year or now.year
        month = month or now.month
        start = f"{year}{month:02d}01"
        end_month = month + 1 if month < 12 else 1
        end_year = year if month < 12 else year + 1
        end = f"{end_year}{end_month:02d}01"
        conditions += [
            ProductRegistration.mod_dt >= start,
            ProductRegistration.mod_dt < end,
        ]
    elif period == "yearly":
        year = year or now.year
        conditions += [
            ProductRegistration.mod_dt >= f"{year}0101",
            ProductRegistration.mod_dt < f"{year + 1}0101",
        ]

    total = (await db.execute(
        select(func.count(ProductRegistration.id)).where(and_(*conditions))
    )).scalar() or 0

    offset = (page - 1) * size
    items_result = await db.execute(
        select(ProductRegistration)
        .where(and_(*conditions))
        .order_by(ProductRegistration.mod_dt.desc(), ProductRegistration.id.desc())
        .offset(offset)
        .limit(size)
    )
    items = list(items_result.scalars().all())

    return RegistrationListResponse(
        total=total,
        page=page,
        size=size,
        items=[RegistrationSchema.model_validate(item) for item in items],
    )
