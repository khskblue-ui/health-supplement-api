from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

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
    """월별/연도별 신고 품목 리스트."""
    # 경쟁사 존재 확인
    comp_result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    if not comp_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Competitor not found")

    conditions = [ProductRegistration.competitor_id == competitor_id]

    if period == "monthly":
        if not year or not month:
            from datetime import datetime, timezone, timedelta
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst)
            year = year or now.year
            month = month or now.month
        start = f"{year}{month:02d}01"
        end_month = month + 1 if month < 12 else 1
        end_year = year if month < 12 else year + 1
        end = f"{end_year}{end_month:02d}01"
        conditions.append(ProductRegistration.change_date >= start)
        conditions.append(ProductRegistration.change_date < end)

    elif period == "yearly":
        if not year:
            from datetime import datetime
            year = datetime.now().year
        start = f"{year}0101"
        end = f"{year + 1}0101"
        conditions.append(ProductRegistration.change_date >= start)
        conditions.append(ProductRegistration.change_date < end)

    # 총 건수
    count_result = await db.execute(
        select(func.count(ProductRegistration.id)).where(and_(*conditions))
    )
    total = count_result.scalar() or 0

    # 페이지 데이터
    offset = (page - 1) * size
    items_result = await db.execute(
        select(ProductRegistration)
        .where(and_(*conditions))
        .order_by(ProductRegistration.change_date.desc(), ProductRegistration.id.desc())
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
