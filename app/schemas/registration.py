from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RegistrationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    competitor_id: int
    prdlst_report_no: str
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    food_type: Optional[str] = None
    btype: Optional[str] = None
    brnch_nm: Optional[str] = None
    mnft_day: Optional[str] = None
    crcl_prd: Optional[str] = None
    mod_dt: Optional[str] = None
    reg_num: Optional[str] = None
    food_histrace_num: Optional[str] = None
    barcode: Optional[str] = None
    source_api: str
    collected_at: datetime


class RegistrationListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[RegistrationSchema]
