import logging
from typing import Any
from app.collectors.base import FoodSafetyAPIClient

logger = logging.getLogger(__name__)

SERVICE_ID = "I0030"


class I0030Collector(FoodSafetyAPIClient):
    """품목제조신고 (I0030) 수집기."""

    async def fetch_by_company(
        self, company_name: str, change_date: str | None = None
    ) -> list[dict[str, Any]]:
        """
        company_name: BSSH_NM (업체명)
        change_date: CHNG_DT (YYYYMMDD), None이면 전체
        """
        params: dict[str, str] = {"BSSH_NM": company_name}
        if change_date:
            params["CHNG_DT"] = change_date

        rows = await self.fetch_all(SERVICE_ID, params)
        logger.info(
            "[I0030] company=%s date=%s → %d rows", company_name, change_date, len(rows)
        )
        return rows

    def parse_row(self, row: dict[str, Any], competitor_id: int) -> dict[str, Any]:
        """API row → ProductRegistration dict."""
        return {
            "competitor_id": competitor_id,
            "license_no": row.get("LCNS_NO", ""),
            "report_no": row.get("PRDLST_REPORT_NO", ""),
            "product_name": row.get("PRDLST_NM", ""),
            "report_date": row.get("PRMS_DT", None),
            "change_date": row.get("CHNG_DT", None),
            "functionality": row.get("PRIMARY_FNCLTY", None),
            "raw_material": row.get("RAWMTRL_NM", None),
            "source_api": SERVICE_ID,
        }
