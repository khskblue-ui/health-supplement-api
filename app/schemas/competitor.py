from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LicenseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    competitor_id: int
    license_no: str
    plant_name: Optional[str] = None
    is_active: bool
    created_at: datetime


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
    updated_at: datetime


class YearlySummarySchema(BaseModel):
    year: int
    count: int


class CompetitorDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_short: str
    total_registrations: int = 0
    licenses: list[LicenseSchema] = []
    monthly_trend: list[MonthlyTrend] = []
    created_at: datetime
    updated_at: datetime
