"""Pydantic schemas for tax return endpoints."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class TaxReturnFields(BaseModel):
    """The 1040 key fields — shared by extract response and confirm request."""
    tax_year: int = Field(..., ge=2000, le=2100, description="Tax year (e.g. 2024)")
    filing_status: Optional[str] = Field(None, description="Single/MFJ/MFS/HOH/QW")
    total_income: Optional[float] = Field(None, description="Line 9 — Total income")
    adjusted_gross_income: Optional[float] = Field(None, description="Line 11 — AGI")
    deduction_type: Optional[str] = Field(None, description="standard or itemized")
    deduction_amount: Optional[float] = Field(None, description="Line 12 — Deduction amount")
    taxable_income: Optional[float] = Field(None, description="Line 15 — Taxable income")
    total_tax: Optional[float] = Field(None, description="Line 24 — Total tax")
    total_credits: Optional[float] = Field(None, description="Lines 19-21 — Total credits")
    federal_withheld: Optional[float] = Field(None, description="Line 25a — Federal tax withheld")
    refund_or_owed: Optional[float] = Field(None, description="Line 34 (refund) or 37 (owed), negative = owed")
    schedule_data: Optional[dict[str, Any]] = Field(None, description="Schedule C/D/E data")


class TaxReturnExtractResponse(BaseModel):
    """Response from PDF upload — unconfirmed extracted data."""
    extraction_id: str
    tax_year: int
    source: str = "pdf_upload"
    fields: TaxReturnFields
    extraction_confidence: float = Field(..., ge=0.0, le=1.0)
    raw_extracted_data: Optional[dict[str, Any]] = None
    needs_review: list[str] = Field(default_factory=list, description="Fields with low confidence")


class TaxReturnConfirmRequest(BaseModel):
    """User confirms (and optionally corrects) extracted data."""
    extraction_id: str
    fields: TaxReturnFields
    source: str = "pdf_upload"


class TaxReturnResponse(BaseModel):
    """A confirmed tax return record."""
    id: str
    user_id: str
    tax_year: int
    source: str
    filing_status: Optional[str]
    total_income: Optional[float]
    adjusted_gross_income: Optional[float]
    deduction_type: Optional[str]
    deduction_amount: Optional[float]
    taxable_income: Optional[float]
    total_tax: Optional[float]
    total_credits: Optional[float]
    federal_withheld: Optional[float]
    refund_or_owed: Optional[float]
    schedule_data: Optional[dict[str, Any]]
    extraction_confidence: Optional[float]
    user_confirmed: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class TaxReturnSummary(BaseModel):
    """Lightweight list item for the years dropdown."""
    tax_year: int
    source: str
    user_confirmed: bool
    adjusted_gross_income: Optional[float]
    total_tax: Optional[float]
    refund_or_owed: Optional[float]
