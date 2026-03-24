from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    name_short: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    licenses: Mapped[list["CompetitorLicense"]] = relationship(
        "CompetitorLicense", back_populates="competitor", lazy="select"
    )
    registrations: Mapped[list["ProductRegistration"]] = relationship(
        "ProductRegistration", back_populates="competitor", lazy="select"
    )
    production_records: Mapped[list["ProductionRecord"]] = relationship(
        "ProductionRecord", back_populates="competitor", lazy="select"
    )


class CompetitorLicense(Base):
    __tablename__ = "competitor_licenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competitor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitors.id"), nullable=False, index=True
    )
    license_no: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    plant_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    competitor: Mapped["Competitor"] = relationship(
        "Competitor", back_populates="licenses"
    )
    registrations: Mapped[list["ProductRegistration"]] = relationship(
        "ProductRegistration", back_populates="license", lazy="select"
    )
