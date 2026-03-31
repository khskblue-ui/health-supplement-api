from fastapi import APIRouter, BackgroundTasks, Query
from app.services.collection_service import CollectionService

router = APIRouter()


@router.post("/collect", summary="수동 데이터 수집 트리거")
async def trigger_collection(
    background_tasks: BackgroundTasks,
    mode: str = Query(default="daily", description="daily | initial"),
    force: bool = Query(default=False, description="initial 모드에서 중복 실행 방지 무시"),
):
    service = CollectionService()
    if mode == "initial":
        # initial 로드는 오래 걸리므로 백그라운드에서 실행 (HTTP 타임아웃 방지)
        background_tasks.add_task(service.run_initial_load, force=force)
        return {"status": "ok", "result": {"type": "initial_load", "message": "started in background"}}
    else:
        result = await service.run_daily_scan()
        return {"status": "ok", "result": result}
