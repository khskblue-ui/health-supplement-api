from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RegistrationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    competitor_id: int
    license_id: Optional[int] = None
    license_no: str
    report_no: str
    product_name: str
    report_date: Optional[str] = None
    change_date: Optional[str] = None
    functionality: Optional[str] = None
    raw_material: Optional[str] = None
    raw_material_detail: Optional[str] = None
    traceability_registered: bool = False
    traceability_reg_num: Optional[str] = None
    traceability_barcode: Optional[str] = None
    traceability_mod_dt: Optional[str] = None
    hfood_yn: Optional[str] = None
    source_api: str
    collected_at: datetime


class RegistrationListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[RegistrationSchema]
