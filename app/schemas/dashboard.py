from pydantic import BaseModel
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
    as_of: str
