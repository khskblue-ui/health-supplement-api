from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MonthlyTrend(BaseModel):
    year_month: str   # "2025-06"
    count: int


class CompetitorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_short: str
    total_registrations: int = 0
    created_at: datetime


class YearlySummarySchema(BaseModel):
    year: int
    count: int


class CompetitorDetailSchema(BaseModel):
    id: int
    name: str
    name_short: str
    total_registrations: int = 0
    monthly_trend: list[MonthlyTrend] = []
    created_at: datetime
