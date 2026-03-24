import logging
from typing import Any
from app.collectors.base import FoodSafetyAPIClient

logger = logging.getLogger(__name__)

SERVICE_ID = "C003"


class C003Collector(FoodSafetyAPIClient):
    """품목제조신고 원재료 (C003) 수집기."""

    async def fetch_by_company(
        self, company_name: str, change_date: str | None = None
    ) -> list[dict[str, Any]]:
        """
        company_name: BSSH_NM (업체명)
        change_date: CHNG_DT (YYYYMMDD)
        """
        params: dict[str, str] = {"BSSH_NM": company_name}
        if change_date:
            params["CHNG_DT"] = change_date

        rows = await self.fetch_all(SERVICE_ID, params)
        logger.info(
            "[C003] company=%s date=%s → %d rows", company_name, change_date, len(rows)
        )
        return rows

    def parse_row(self, row: dict[str, Any]) -> dict[str, Any]:
        """C003 row → raw_material_detail 업데이트용 dict."""
        return {
            "report_no": row.get("PRDLST_REPORT_NO", ""),
            "license_no": row.get("LCNS_NO", ""),
            "raw_material_detail": row.get("RAWMTRL_NM", None),
            # C003에서 추가로 가져올 수 있는 필드
            "functionality": row.get("PRIMARY_FNCLTY", None),
        }
