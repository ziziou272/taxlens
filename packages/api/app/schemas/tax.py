"""Tax calculation schemas."""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ISOExercise(BaseModel):
    shares: int = 0
    strike_price: float = 0
    fmv_at_exercise: float = 0


class NSOExercise(BaseModel):
    shares: int = 0
    strike_price: float = 0
    fmv_at_exercise: float = 0


class ESPPSale(BaseModel):
    shares: int = 0
    purchase_price: float = 0
    sale_price: float = 0
    holding_period_months: int = 0


class TaxInput(BaseModel):
    filing_status: str = "single"
    wages: float = 0
    rsu_income: float = 0
    iso_exercises: list[ISOExercise] = Field(default_factory=list)
    nso_exercises: list[NSOExercise] = Field(default_factory=list)
    espp_sales: list[ESPPSale] = Field(default_factory=list)
    capital_gains_short: float = 0
    capital_gains_long: float = 0
    qualified_dividends: float = 0
    interest_income: float = 0
    state: Optional[str] = "CA"
    itemized_deductions: Optional[float] = None
    federal_withheld: float = 0
    state_withheld: float = 0


class WithholdingGapInput(BaseModel):
    filing_status: str = "single"
    wages: float = 0
    rsu_income: float = 0
    capital_gains_long: float = 0
    state: Optional[str] = "CA"
    ytd_federal_withheld: float = 0
    ytd_state_withheld: float = 0


class TaxBreakdownResponse(BaseModel):
    year: int = 2025
    filing_status: str
    total_income: float
    taxable_income: float
    federal_tax: float
    federal_tax_on_ordinary: float
    federal_tax_on_ltcg: float
    amt_owed: float = 0
    social_security_tax: float
    medicare_tax: float
    additional_medicare_tax: float = 0
    niit: float = 0
    state_tax: float = 0
    state_code: Optional[str] = None
    total_tax: float
    effective_rate: float
    marginal_rate: float
    deduction_used: float
    balance_due: float = 0
    warnings: list[str] = Field(default_factory=list)


class WithholdingGapResponse(BaseModel):
    projected_total_tax: float
    ytd_withheld: float
    gap: float
    gap_percentage: float
    quarterly_payment_needed: float
    warnings: list[str] = Field(default_factory=list)
