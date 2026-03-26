from sqlalchemy import String, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class ProductRegistration(Base):
    __tablename__ = "product_registrations"
    __table_args__ = (
        UniqueConstraint("food_histrace_num", name="uq_histrace_num"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competitor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitors.id"), nullable=False, index=True
    )

    # I0320 핵심 필드
    prdlst_report_no: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    product_name: Mapped[str | None] = mapped_column(String(500))
    product_type: Mapped[str | None] = mapped_column(String(100))   # PDT_TYPE (비타민D 등)
    food_type: Mapped[str | None] = mapped_column(String(20))        # 건기 / 식품
    btype: Mapped[str | None] = mapped_column(String(100))           # 건강기능식품전문제조업 등
    brnch_nm: Mapped[str | None] = mapped_column(String(200))        # 공장명
    mnft_day: Mapped[str | None] = mapped_column(String(8))          # YYYYMMDD 제조일
    crcl_prd: Mapped[str | None] = mapped_column(String(8))          # YYYYMMDD 유통기한
    mod_dt: Mapped[str | None] = mapped_column(String(8), index=True) # YYYYMMDD (월별 집계 기준)
    reg_num: Mapped[str | None] = mapped_column(String(50))
    food_histrace_num: Mapped[str | None] = mapped_column(String(50), index=True)
    barcode: Mapped[str | None] = mapped_column(String(100))
    source_api: Mapped[str] = mapped_column(String(10), default="I0320")

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    competitor: Mapped["Competitor"] = relationship(
        "Competitor", back_populates="registrations"
    )
