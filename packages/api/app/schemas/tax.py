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
    # Filing basics
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

    # Legacy itemized deductions (pre-computed total; ignored when components provided)
    itemized_deductions: Optional[float] = None

    # --- Itemized deduction components ---
    mortgage_interest: float = 0
    mortgage_loan_balance: float = 0          # For $750K proportional cap
    salt_paid: float = 0                      # State/local taxes paid
    charitable: float = 0                     # Charitable contributions
    medical_expenses: float = 0               # Total medical expenses paid

    # --- Above-the-line deductions ---
    contributions_401k: float = 0
    ira_contributions: float = 0
    hsa_contributions: float = 0
    student_loan_interest: float = 0
    age_over_50: bool = False                 # Enables catch-up limits
    hsa_family_coverage: bool = False         # Family HDHP → higher HSA limit

    # --- Dependents / Credits ---
    num_children_under_17: int = 0            # Qualifying children for CTC
    num_other_dependents: int = 0             # Other dependents ($500 credit)

    # --- Education Credits ---
    education_expenses: float = 0
    education_type: str = "aotc"              # "aotc" or "llc"
    num_students: int = 1

    # Withholding
    federal_withheld: float = 0
    state_withheld: float = 0


class ItemizedDeductionsDetailResponse(BaseModel):
    mortgage_interest: float = 0
    salt: float = 0           # After SALT cap
    salt_paid: float = 0      # Before cap
    charitable: float = 0
    medical: float = 0        # After 7.5% AGI floor
    medical_paid: float = 0   # Before floor
    total: float = 0


class AboveTheLineDeductionsResponse(BaseModel):
    contributions_401k: float = 0
    ira_contributions: float = 0
    hsa_contributions: float = 0
    student_loan_interest: float = 0
    total: float = 0


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
    agi: float = 0                                    # After above-the-line deductions
    taxable_income: float
    deduction_used: float

    # Above-the-line deductions breakdown
    above_the_line_deductions: AboveTheLineDeductionsResponse = Field(
        default_factory=AboveTheLineDeductionsResponse
    )

    # Itemized deductions breakdown
    itemized_deductions_detail: ItemizedDeductionsDetailResponse = Field(
        default_factory=ItemizedDeductionsDetailResponse
    )

    # Federal tax (before credits)
    federal_tax: float
    federal_tax_on_ordinary: float
    federal_tax_on_ltcg: float
    amt_owed: float = 0

    # Credits
    child_tax_credit: float = 0
    other_dependent_credit: float = 0
    actc: float = 0                                   # Additional CTC (refundable)
    eitc: float = 0                                   # EITC (refundable)
    education_credit: float = 0                       # Non-refundable portion
    education_credit_refundable: float = 0            # Refundable portion (AOTC)
    total_credits: float = 0

    # Payroll taxes
    social_security_tax: float
    medicare_tax: float
    additional_medicare_tax: float = 0
    niit: float = 0

    # State
    state_tax: float = 0
    state_code: Optional[str] = None

    # Totals
    total_tax: float
    effective_rate: float
    marginal_rate: float
    balance_due: float = 0
    warnings: list[str] = Field(default_factory=list)


class WithholdingGapResponse(BaseModel):
    projected_total_tax: float
    ytd_withheld: float
    gap: float
    gap_percentage: float
    quarterly_payment_needed: float
    warnings: list[str] = Field(default_factory=list)
