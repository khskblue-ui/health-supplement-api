import logging
from typing import Any
from app.collectors.base import FoodSafetyAPIClient
from app.config import settings

logger = logging.getLogger(__name__)

SERVICE_ID = "I0320"


class I0320Collector(FoodSafetyAPIClient):
    """이력추적관리 등록현황 (I0320) 수집기."""

    def __init__(self):
        super().__init__(api_key=settings.FOOD_SAFETY_API_KEY_I0320 or settings.FOOD_SAFETY_API_KEY)

    async def fetch_by_company(
        self, company_name: str, mod_date: str | None = None
    ) -> list[dict[str, Any]]:
        """
        company_name: BRNCH_NM 부분 매칭 (예: '노바렉스')
        mod_date: MOD_DT YYYYMMDD 필터 (None이면 전체)
        """
        params: dict[str, str] = {"BRNCH_NM": company_name}
        if mod_date:
            params["MOD_DT"] = mod_date

        rows = await self.fetch_all(SERVICE_ID, params)
        logger.info("[I0320] company=%s date=%s → %d rows", company_name, mod_date, len(rows))
        return rows

    def parse_row(self, row: dict[str, Any], competitor_id: int) -> dict[str, Any]:
        """I0320 API row → ProductRegistration dict."""
        barcode = row.get("PDT_BARCD", "") or None
        return {
            "competitor_id": competitor_id,
            "prdlst_report_no": row.get("PRDLST_REPORT_NO", ""),
            "product_name": row.get("PDT_NM", ""),
            "product_type": row.get("PDT_TYPE", ""),
            "food_type": row.get("FOOD_TYPE", ""),
            "btype": row.get("BTYPE", ""),
            "brnch_nm": row.get("BRNCH_NM", ""),
            "mnft_day": row.get("MNFT_DAY", "") or None,
            "crcl_prd": row.get("CRCL_PRD", "") or None,
            "mod_dt": row.get("MOD_DT", "") or None,
            "reg_num": row.get("REG_NUM", "") or None,
            "food_histrace_num": row.get("FOOD_HISTRACE_NUM", "") or None,
            "barcode": barcode,
            "source_api": SERVICE_ID,
        }
