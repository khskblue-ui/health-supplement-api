import logging
from typing import Any
from app.collectors.base import FoodSafetyAPIClient

logger = logging.getLogger(__name__)

SERVICE_ID = "I0320"


class I0320Collector(FoodSafetyAPIClient):
    """이력추적관리 등록현황 (I0320) 수집기."""

    async def fetch_by_company(
        self, company_name: str, mod_date: str | None = None
    ) -> list[dict[str, Any]]:
        """
        company_name: BRNCH_NM (업체명)
        mod_date: MOD_DT (YYYYMMDD)
        """
        params: dict[str, str] = {"BRNCH_NM": company_name}
        if mod_date:
            params["MOD_DT"] = mod_date

        rows = await self.fetch_all(SERVICE_ID, params)
        logger.info(
            "[I0320] company=%s date=%s → %d rows", company_name, mod_date, len(rows)
        )
        return rows

    def parse_row(self, row: dict[str, Any]) -> dict[str, Any]:
        """I0320 row → traceability 업데이트용 dict."""
        return {
            "report_no": row.get("PRDLST_REPORT_NO", ""),
            "license_no": row.get("LCNS_NO", ""),
            "traceability_registered": True,
            "traceability_reg_num": row.get("REG_NO", None),
            "traceability_barcode": row.get("BARCODE_NO", None),
            "traceability_mod_dt": row.get("MOD_DT", None),
            "hfood_yn": row.get("HFOOD_YN", None),
        }
