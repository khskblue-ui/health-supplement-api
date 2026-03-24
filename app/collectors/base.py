import httpx
import asyncio
import logging
from typing import Any
from app.config import settings

logger = logging.getLogger(__name__)

FOOD_SAFETY_BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
PAGE_SIZE = 1000
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30


class FoodSafetyAPIClient:
    """식품안전나라 공공 API 공통 클라이언트."""

    def __init__(self):
        self.api_key = settings.FOOD_SAFETY_API_KEY
        self.base_url = FOOD_SAFETY_BASE_URL

    def _build_url(self, service_id: str, start: int, end: int) -> str:
        return f"{self.base_url}/{self.api_key}/{service_id}/json/{start}/{end}"

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        service_id: str,
        start: int,
        end: int,
        params: dict[str, str],
    ) -> dict[str, Any]:
        url = self._build_url(service_id, start, end)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.get(url, params=params, timeout=TIMEOUT_SECONDS)
                resp.raise_for_status()
                data = resp.json()
                return data
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "HTTP error %s on %s (attempt %d/%d)",
                    e.response.status_code, url, attempt, MAX_RETRIES
                )
            except (httpx.RequestError, Exception) as e:
                logger.warning(
                    "Request error on %s (attempt %d/%d): %s",
                    url, attempt, MAX_RETRIES, e
                )
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** attempt)
        return {}

    async def fetch_all(
        self,
        service_id: str,
        params: dict[str, str],
    ) -> list[dict[str, Any]]:
        """전체 페이지를 순차 수집하여 row 목록 반환."""
        if not self.api_key:
            logger.error("FOOD_SAFETY_API_KEY is not configured — skipping collection")
            return []

        all_rows: list[dict[str, Any]] = []
        async with httpx.AsyncClient() as client:
            start = 1
            while True:
                end = start + PAGE_SIZE - 1
                data = await self._fetch_page(client, service_id, start, end, params)
                service_data = data.get(service_id, {})
                result_code = (
                    service_data.get("RESULT", {}).get("CODE", "")
                    if isinstance(service_data.get("RESULT"), dict)
                    else ""
                )
                # INFO-000: 정상, INFO-200: 데이터 없음
                if result_code == "INFO-200" or not service_data:
                    break
                rows = service_data.get("row", [])
                if not rows:
                    break
                all_rows.extend(rows)
                logger.info(
                    "[%s] fetched %d rows (start=%d)", service_id, len(rows), start
                )
                if len(rows) < PAGE_SIZE:
                    break
                start += PAGE_SIZE
        return all_rows
