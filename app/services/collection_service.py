import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.models.collection_job import CollectionJob
from app.collectors.i0320_collector import I0320Collector

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self):
        self.i0320 = I0320Collector()

    async def _get_competitors(self, session: AsyncSession) -> list[Competitor]:
        result = await session.execute(select(Competitor).order_by(Competitor.id))
        return list(result.scalars().all())

    async def _upsert_registrations(
        self, session: AsyncSession, records: list[dict[str, Any]]
    ) -> int:
        if not records:
            return 0
        # food_histrace_num이 None인 경우 중복 허용 (NULL은 UNIQUE 무시)
        valid = [r for r in records if r.get("food_histrace_num")]
        skip = [r for r in records if not r.get("food_histrace_num")]

        inserted = 0
        if valid:
            stmt = pg_insert(ProductRegistration).values(valid)
            stmt = stmt.on_conflict_do_nothing(constraint="uq_histrace_num")
            result = await session.execute(stmt)
            inserted += result.rowcount or 0

        if skip:
            for rec in skip:
                session.add(ProductRegistration(**rec))
            inserted += len(skip)

        await session.flush()
        return inserted

    async def _create_job(self, session: AsyncSession, job_type: str, target_date: str | None) -> CollectionJob:
        job = CollectionJob(
            job_type=job_type,
            source_api="I0320",
            target_date=target_date,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        session.add(job)
        await session.flush()
        return job

    async def _finish_job(self, session: AsyncSession, job: CollectionJob, records_found: int, error: str | None = None) -> None:
        job.records_found = records_found
        job.status = "failed" if error else "completed"
        job.error_message = error
        job.completed_at = datetime.now(timezone.utc)
        await session.flush()

    async def run_daily_scan(self, target_date: str | None = None) -> dict[str, Any]:
        """일일 수집: I0320 mod_dt 기준 신규 등록 감지."""
        if not target_date:
            kst = timezone(timedelta(hours=9))
            target_date = datetime.now(kst).strftime("%Y%m%d")

        logger.info("Starting daily I0320 scan for date: %s", target_date)
        total = 0

        async with AsyncSessionLocal() as session:
            competitors = await self._get_competitors(session)
            if not competitors:
                logger.warning("No competitors found in DB")
                return {"target_date": target_date, "total": 0}

            job = await self._create_job(session, "daily", target_date)
            try:
                for comp in competitors:
                    rows = await self.i0320.fetch_by_company(comp.name, target_date)
                    records = [self.i0320.parse_row(r, comp.id) for r in rows]
                    inserted = await self._upsert_registrations(session, records)
                    total += inserted
                    logger.info("[I0320] %s → %d rows, %d inserted", comp.name, len(rows), inserted)
                await self._finish_job(session, job, total)
            except Exception as e:
                logger.exception("I0320 daily scan failed")
                await self._finish_job(session, job, total, str(e))

            await session.commit()

        logger.info("Daily scan complete: total=%d", total)
        return {"target_date": target_date, "total": total}

    async def run_initial_load(self) -> dict[str, Any]:
        """전체 이력 초기 적재 (날짜 필터 없이 전체 수집)."""
        logger.info("Starting I0320 initial load")
        total = 0

        async with AsyncSessionLocal() as session:
            competitors = await self._get_competitors(session)
            job = await self._create_job(session, "initial", None)
            try:
                for comp in competitors:
                    rows = await self.i0320.fetch_by_company(comp.name)
                    records = [self.i0320.parse_row(r, comp.id) for r in rows]
                    inserted = await self._upsert_registrations(session, records)
                    total += inserted
                    logger.info("[I0320 initial] %s → %d rows, %d inserted", comp.name, len(rows), inserted)
                await self._finish_job(session, job, total)
            except Exception as e:
                logger.exception("I0320 initial load failed")
                await self._finish_job(session, job, total, str(e))

            await session.commit()

        return {"type": "initial_load", "total": total}
