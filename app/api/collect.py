from fastapi import APIRouter, Query
from app.services.collection_service import CollectionService

router = APIRouter()


@router.post("/collect", summary="수동 데이터 수집 트리거")
async def trigger_collection(
    mode: str = Query(default="daily", description="daily | initial"),
    force: bool = Query(default=False, description="initial 모드에서 중복 실행 방지 무시"),
):
    service = CollectionService()
    if mode == "initial":
        result = await service.run_initial_load(force=force)
    else:
        result = await service.run_daily_scan()
    return {"status": "ok", "result": result}
