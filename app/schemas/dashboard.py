from pydantic import BaseModel
from typing import Optional
from app.schemas.registration import RegistrationSchema


class CompetitorSummary(BaseModel):
    id: int
    name: str
    name_short: str
    recent_count: int        # 최근 30일
    last_7_days_count: int   # 최근 7일
    latest_products: list[RegistrationSchema] = []


class DashboardResponse(BaseModel):
    competitors: list[CompetitorSummary]
    as_of: str   # ISO datetime string


class ProductionRecordSchema(BaseModel):
    id: int
    competitor_id: int
    license_no: str
    product_name: str
    product_type: Optional[str] = None
    report_year: str
    production_qty_kg: Optional[float] = None
    production_capacity_kg: Optional[float] = None


class ProductionAnalysisResponse(BaseModel):
    year: str
    competitor_id: Optional[int] = None
    records: list[ProductionRecordSchema]
    total: int
