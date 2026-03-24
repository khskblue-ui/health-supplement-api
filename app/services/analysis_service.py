import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.models.production_record import ProductionRecord

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))


class AnalysisService:

    async def get_dashboard_data(self, session: AsyncSession) -> dict:
        now = datetime.now(KST)
        date_30d = (now - timedelta(days=30)).strftime("%Y%m%d")
        date_7d = (now - timedelta(days=7)).strftime("%Y%m%d")

        competitors_result = await session.execute(
            select(Competitor).order_by(Competitor.id)
        )
        competitors = list(competitors_result.scalars().all())

        summaries = []
        for comp in competitors:
            # 최근 30일 count
            r30 = await session.execute(
                select(func.count(ProductRegistration.id)).where(
                    and_(
                        ProductRegistration.competitor_id == comp.id,
                        ProductRegistration.change_date >= date_30d,
                    )
                )
            )
            recent_count = r30.scalar() or 0

            # 최근 7일 count
            r7 = await session.execute(
                select(func.count(ProductRegistration.id)).where(
                    and_(
                        ProductRegistration.competitor_id == comp.id,
                        ProductRegistration.change_date >= date_7d,
                    )
                )
            )
            last_7_days_count = r7.scalar() or 0

            # 최신 5건
            latest_result = await session.execute(
                select(ProductRegistration)
                .where(ProductRegistration.competitor_id == comp.id)
                .order_by(ProductRegistration.change_date.desc(), ProductRegistration.id.desc())
                .limit(5)
            )
            latest_products = list(latest_result.scalars().all())

            summaries.append(
                {
                    "id": comp.id,
                    "name": comp.name,
                    "name_short": comp.name_short,
                    "recent_count": recent_count,
                    "last_7_days_count": last_7_days_count,
                    "latest_products": latest_products,
                }
            )

        return {
            "competitors": summaries,
            "as_of": now.isoformat(),
        }

    async def get_monthly_trend(
        self, session: AsyncSession, competitor_id: int, months: int = 12
    ) -> list[dict]:
        now = datetime.now(KST)
        result = []
        for i in range(months - 1, -1, -1):
            # 월 계산
            month_dt = now.replace(day=1) - timedelta(days=30 * i)
            year = month_dt.year
            month = month_dt.month
            start = f"{year}{month:02d}01"
            # 해당 월의 마지막 날
            if month == 12:
                end = f"{year + 1}0101"
            else:
                end = f"{year}{month + 1:02d}01"

            r = await session.execute(
                select(func.count(ProductRegistration.id)).where(
                    and_(
                        ProductRegistration.competitor_id == competitor_id,
                        ProductRegistration.change_date >= start,
                        ProductRegistration.change_date < end,
                    )
                )
            )
            count = r.scalar() or 0
            result.append({"year_month": f"{year}-{month:02d}", "count": count})
        return result

    async def get_production_analysis(
        self,
        session: AsyncSession,
        year: str,
        competitor_id: int | None = None,
    ) -> dict:
        query = select(ProductionRecord).where(ProductionRecord.report_year == year)
        if competitor_id:
            query = query.where(ProductionRecord.competitor_id == competitor_id)
        query = query.order_by(ProductionRecord.competitor_id, ProductionRecord.product_name)

        result = await session.execute(query)
        records = list(result.scalars().all())

        return {
            "year": year,
            "competitor_id": competitor_id,
            "records": records,
            "total": len(records),
        }
