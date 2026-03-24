from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class ProductionRecord(Base):
    __tablename__ = "production_records"
    __table_args__ = (
        UniqueConstraint("license_no", "product_name", "report_year", name="uq_production_record"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competitor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitors.id"), nullable=False, index=True
    )
    license_no: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    product_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    report_year: Mapped[str] = mapped_column(String(4), nullable=False, index=True)
    production_qty_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    production_capacity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    competitor: Mapped["Competitor"] = relationship(
        "Competitor", back_populates="production_records"
    )
