"""Tax return model — stores previous year's filed 1040 data."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaxReturn(Base):
    __tablename__ = "tax_returns_local"  # 'tax_returns' lives in Supabase; local mirror for SQLite dev

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True)
    tax_year: Mapped[int] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(String, default="pdf_upload")  # pdf_upload | manual | irs_transcript

    # 1040 Key Fields
    filing_status: Mapped[str | None] = mapped_column(String, nullable=True)
    total_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    adjusted_gross_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    deduction_type: Mapped[str | None] = mapped_column(String, nullable=True)   # 'standard' | 'itemized'
    deduction_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    taxable_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_tax: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_credits: Mapped[float | None] = mapped_column(Float, nullable=True)
    federal_withheld: Mapped[float | None] = mapped_column(Float, nullable=True)
    refund_or_owed: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Rich/raw data stored as JSON strings
    schedule_data: Mapped[str | None] = mapped_column(Text, nullable=True)       # JSON
    raw_extracted_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Upload metadata
    pdf_storage_path: Mapped[str | None] = mapped_column(String, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
