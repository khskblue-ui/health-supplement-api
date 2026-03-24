from sqlalchemy import (
    String, Boolean, Integer, ForeignKey, DateTime, Text,
    func, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class ProductRegistration(Base):
    __tablename__ = "product_registrations"
    __table_args__ = (
        UniqueConstraint("license_no", "report_no", name="uq_license_report"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competitor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitors.id"), nullable=False, index=True
    )
    license_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("competitor_licenses.id"), nullable=True, index=True
    )

    # 기본 신고 정보
    license_no: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    report_no: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    report_date: Mapped[str | None] = mapped_column(String(8), nullable=True)   # YYYYMMDD
    change_date: Mapped[str | None] = mapped_column(String(8), nullable=True)   # YYYYMMDD

    # 기능성 및 원재료
    functionality: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_material: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_material_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # I0320 이력추적 교차확인
    traceability_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    traceability_reg_num: Mapped[str | None] = mapped_column(String(100), nullable=True)
    traceability_barcode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    traceability_mod_dt: Mapped[str | None] = mapped_column(String(8), nullable=True)
    hfood_yn: Mapped[str | None] = mapped_column(String(1), nullable=True)

    # 메타
    source_api: Mapped[str] = mapped_column(String(10), nullable=False, default="I0030")
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    competitor: Mapped["Competitor"] = relationship(
        "Competitor", back_populates="registrations"
    )
    license: Mapped["CompetitorLicense | None"] = relationship(
        "CompetitorLicense", back_populates="registrations"
    )
