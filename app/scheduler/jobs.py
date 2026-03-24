import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.collection_service import CollectionService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


async def daily_collection_job():
    """매일 06:00 KST (21:00 UTC 전날) 실행되는 일일 수집 잡."""
    logger.info("Starting scheduled daily collection job")
    service = CollectionService()
    try:
        result = await service.run_daily_scan()
        logger.info("Daily collection completed: %s", result)
    except Exception:
        logger.exception("Daily collection job failed")


def setup_scheduler() -> AsyncIOScheduler:
    """스케줄러 잡 등록 후 반환."""
    # 매일 21:00 UTC = 06:00 KST
    scheduler.add_job(
        daily_collection_job,
        trigger=CronTrigger(hour=21, minute=0, timezone="UTC"),
        id="daily_collection",
        name="Daily competitor product registration scan",
        replace_existing=True,
        misfire_grace_time=3600,  # 1시간 이내 지연 허용
    )
    logger.info("Scheduler configured: daily_collection at 21:00 UTC")
    return scheduler
