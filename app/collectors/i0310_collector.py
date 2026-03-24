import logging
from typing import Any
from app.collectors.base import FoodSafetyAPIClient

logger = logging.getLogger(__name__)

SERVICE_ID = "I0310"


class I0310Collector(FoodSafetyAPIClient):
    """연간생산실적 (I0310) 수집기."""

    async def fetch_by_company(
        self, company_name: str, report_year: str | None = None
    ) -> list[dict[str, Any]]:
        """
        company_name: BSSH_NM (업체명)
        report_year: PRDT_YY (연도, YYYY)
        """
        params: dict[str, str] = {"BSSH_NM": company_name}
        if report_year:
            params["PRDT_YY"] = report_year

        rows = await self.fetch_all(SERVICE_ID, params)
        logger.info(
            "[I0310] company=%s year=%s → %d rows", company_name, report_year, len(rows)
        )
        return rows

    def parse_row(self, row: dict[str, Any], competitor_id: int) -> dict[str, Any]:
        """I0310 row → ProductionRecord dict."""
        try:
            qty = float(row.get("PRDT_QY", 0) or 0)
        except (ValueError, TypeError):
            qty = None
        try:
            cap = float(row.get("PRDT_CPCTY", 0) or 0)
        except (ValueError, TypeError):
            cap = None

        return {
            "competitor_id": competitor_id,
            "license_no": row.get("LCNS_NO", ""),
            "product_name": row.get("PRDLST_NM", ""),
            "product_type": row.get("PRDLST_TP", None),
            "report_year": row.get("PRDT_YY", ""),
            "production_qty_kg": qty,
            "production_capacity_kg": cap,
        }
