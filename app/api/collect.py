from fastapi import APIRouter
from app.services.collection_service import CollectionService

router = APIRouter()


@router.post("/collect", summary="수동 데이터 수집 트리거")
async def trigger_collection():
    service = CollectionService()
    result = await service.run_daily_scan()
    return {"status": "ok", "result": result}
