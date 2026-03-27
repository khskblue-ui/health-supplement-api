import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.api.router import api_router
from app.scheduler.jobs import setup_scheduler
from app.database import engine, AsyncSessionLocal, Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

COMPETITORS_SEED = [
    {"id": 1, "name": "노바렉스(주)", "name_short": "노바렉스"},
    {"id": 2, "name": "콜마비앤에이치(주)", "name_short": "콜마비앤에이치"},
    {"id": 3, "name": "코스맥스바이오(주)", "name_short": "코스맥스바이오"},
    {"id": 4, "name": "코스맥스엔비티(주)", "name_short": "코스맥스엔비티"},
]


async def _init_db():
    """테이블 생성 및 경쟁사 시드 데이터 삽입."""
    import app.models  # noqa: F401 – register all models with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB tables ensured")

    from app.models.competitor import Competitor
    async with AsyncSessionLocal() as session:
        for c in COMPETITORS_SEED:
            existing = await session.execute(select(Competitor).where(Competitor.id == c["id"]))
            if not existing.scalar_one_or_none():
                session.add(Competitor(id=c["id"], name=c["name"], name_short=c["name_short"]))
        await session.commit()
    logger.info("Competitor seed data ensured")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작
    logger.info("Starting %s (env=%s)", settings.APP_TITLE, settings.ENVIRONMENT)
    await _init_db()
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("APScheduler started")
    yield
    # 종료
    scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="건강기능식품 경쟁사 모니터링 백엔드 API",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터
app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
