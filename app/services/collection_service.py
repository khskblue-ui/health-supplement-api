import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.competitor import Competitor
from app.models.registration import ProductRegistration
from app.models.collection_job import CollectionJob
from app.models.production_record import ProductionRecord
from app.collectors.i0030_collector import I0030Collector
from app.collectors.c003_collector import C003Collector
from app.collectors.i0320_collector import I0320Collector
from app.collectors.i0310_collector import I0310Collector

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self):
        self.i0030 = I0030Collector()
        self.c003 = C003Collector()
        self.i0320 = I0320Collector()
        self.i0310 = I0310Collector()

    async def _get_competitors(self, session: AsyncSession) -> list[Competitor]:
        result = await session.execute(select(Competitor).order_by(Competitor.id))
        return list(result.scalars().all())

    async def _upsert_registrations(
        self, session: AsyncSession, records: list[dict[str, Any]]
    ) -> int:
        if not records:
            return 0
        stmt = pg_insert(ProductRegistration).values(records)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_license_report")
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount or 0

    async def _update_raw_material(
        self, session: AsyncSession, c003_rows: list[dict[str, Any]]
    ) -> None:
        for row in c003_rows:
            report_no = row.get("report_no", "")
            license_no = row.get("license_no", "")
            raw_material_detail = row.get("raw_material_detail")
            if not report_no or not raw_material_detail:
                continue
            await session.execute(
                update(ProductRegistration)
                .where(
                    ProductRegistration.report_no == report_no,
                    ProductRegistration.license_no == license_no,
                )
                .values(raw_material_detail=raw_material_detail)
            )

    async def _update_traceability(
        self, session: AsyncSession, i0320_rows: list[dict[str, Any]]
    ) -> None:
        for row in i0320_rows:
            report_no = row.get("report_no", "")
            if not report_no:
                continue
            # I0320 응답에는 LCNS_NO 없음 → report_no 단독 매칭
            await session.execute(
                update(ProductRegistration)
                .where(ProductRegistration.report_no == report_no)
                .values(
                    traceability_registered=True,
                    traceability_reg_num=row.get("traceability_reg_num"),
                    traceability_barcode=row.get("traceability_barcode"),
                    traceability_mod_dt=row.get("traceability_mod_dt"),
                    hfood_yn=row.get("hfood_yn"),
                )
            )

    async def _create_job(
        self,
        session: AsyncSession,
        job_type: str,
        source_api: str,
        target_date: str | None,
    ) -> CollectionJob:
        job = CollectionJob(
            job_type=job_type,
            source_api=source_api,
            target_date=target_date,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        session.add(job)
        await session.flush()
        return job

    async def _finish_job(
        self,
        session: AsyncSession,
        job: CollectionJob,
        records_found: int,
        error: str | None = None,
    ) -> None:
        job.records_found = records_found
        job.status = "failed" if error else "completed"
        job.error_message = error
        job.completed_at = datetime.now(timezone.utc)
        await session.flush()

    async def run_daily_scan(self, target_date: str | None = None) -> dict[str, Any]:
        """
        일일 수집 실행.
        target_date: YYYYMMDD 형식. None이면 오늘 날짜.
        """
        if not target_date:
            kst = timezone(timedelta(hours=9))
            target_date = datetime.now(kst).strftime("%Y%m%d")

        logger.info("Starting daily scan for date: %s", target_date)
        summary: dict[str, Any] = {"target_date": target_date, "apis": {}}

        async with AsyncSessionLocal() as session:
            competitors = await self._get_competitors(session)
            if not competitors:
                logger.warning("No competitors found in DB")
                return summary

            # --- I0030 수집 ---
            i0030_job = await self._create_job(session, "daily", "I0030", target_date)
            total_i0030 = 0
            try:
                for comp in competitors:
                    rows = await self.i0030.fetch_by_company(comp.name, target_date)
                    records = [
                        self.i0030.parse_row(r, comp.id) for r in rows
                    ]
                    inserted = await self._upsert_registrations(session, records)
                    total_i0030 += inserted
                await self._finish_job(session, i0030_job, total_i0030)
            except Exception as e:
                logger.exception("I0030 collection failed")
                await self._finish_job(session, i0030_job, total_i0030, str(e))
            summary["apis"]["I0030"] = total_i0030

            # --- C003 수집 ---
            c003_job = await self._create_job(session, "daily", "C003", target_date)
            total_c003 = 0
            try:
                for comp in competitors:
                    rows = await self.c003.fetch_by_company(comp.name, target_date)
                    parsed = [self.c003.parse_row(r) for r in rows]
                    await self._update_raw_material(session, parsed)
                    total_c003 += len(parsed)
                await self._finish_job(session, c003_job, total_c003)
            except Exception as e:
                logger.exception("C003 collection failed")
                await self._finish_job(session, c003_job, total_c003, str(e))
            summary["apis"]["C003"] = total_c003

            # --- I0320 수집 ---
            i0320_job = await self._create_job(session, "daily", "I0320", target_date)
            total_i0320 = 0
            try:
                for comp in competitors:
                    rows = await self.i0320.fetch_by_company(comp.name, target_date)
                    parsed = [self.i0320.parse_row(r) for r in rows]
                    await self._update_traceability(session, parsed)
                    total_i0320 += len(parsed)
                await self._finish_job(session, i0320_job, total_i0320)
            except Exception as e:
                logger.exception("I0320 collection failed")
                await self._finish_job(session, i0320_job, total_i0320, str(e))
            summary["apis"]["I0320"] = total_i0320

            await session.commit()

        logger.info("Daily scan complete: %s", summary)
        return summary

    async def run_initial_load(self) -> dict[str, Any]:
        """전체 이력 초기 적재 (날짜 필터 없이 전체 수집)."""
        logger.info("Starting initial load")
        summary: dict[str, Any] = {"type": "initial_load", "apis": {}}

        async with AsyncSessionLocal() as session:
            competitors = await self._get_competitors(session)

            i0030_job = await self._create_job(session, "initial", "I0030", None)
            total = 0
            try:
                for comp in competitors:
                    rows = await self.i0030.fetch_by_company(comp.name)
                    records = [self.i0030.parse_row(r, comp.id) for r in rows]
                    inserted = await self._upsert_registrations(session, records)
                    total += inserted
                await self._finish_job(session, i0030_job, total)
            except Exception as e:
                logger.exception("Initial I0030 load failed")
                await self._finish_job(session, i0030_job, total, str(e))
            summary["apis"]["I0030"] = total

            await session.commit()

        return summary

    async def run_production_collection(self, report_year: str | None = None) -> dict[str, Any]:
        """I0310 연간생산실적 수집."""
        if not report_year:
            report_year = str(datetime.now().year - 1)  # 전년도 기본

        logger.info("Collecting I0310 production records for year: %s", report_year)
        summary: dict[str, Any] = {"year": report_year}

        async with AsyncSessionLocal() as session:
            competitors = await self._get_competitors(session)

            job = await self._create_job(session, "annual", "I0310", report_year)
            total = 0
            try:
                for comp in competitors:
                    rows = await self.i0310.fetch_by_company(comp.name, report_year)
                    records = [self.i0310.parse_row(r, comp.id) for r in rows]
                    if records:
                        stmt = pg_insert(ProductionRecord).values(records)
                        stmt = stmt.on_conflict_do_nothing(constraint="uq_production_record")
                        await session.execute(stmt)
                        total += len(records)
                await self._finish_job(session, job, total)
            except Exception as e:
                logger.exception("I0310 collection failed")
                await self._finish_job(session, job, total, str(e))

            await session.commit()

        summary["total"] = total
        return summary
