"""
Core data models for TaxLens Engine.

All monetary values use Decimal for exact arithmetic.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FilingStatus(str, Enum):
    """IRS filing status."""
    SINGLE = "single"
    MARRIED_JOINTLY = "married_jointly"
    MARRIED_SEPARATELY = "married_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"


class EquityType(str, Enum):
    """Types of equity compensation."""
    RSU = "rsu"  # Restricted Stock Units
    ISO = "iso"  # Incentive Stock Options
    NSO = "nso"  # Non-Qualified Stock Options
    ESPP = "espp"  # Employee Stock Purchase Plan


class TaxYear(BaseModel):
    """Tax year configuration with brackets and limits."""
    year: int = 2025
    
    # Standard deductions
    standard_deduction_single: Decimal = Decimal("15000")
    standard_deduction_married_jointly: Decimal = Decimal("30000")
    standard_deduction_married_separately: Decimal = Decimal("15000")
    standard_deduction_head_of_household: Decimal = Decimal("22500")
    
    # Social Security
    social_security_wage_base: Decimal = Decimal("176100")
    social_security_rate: Decimal = Decimal("0.062")
    medicare_rate: Decimal = Decimal("0.0145")
    additional_medicare_threshold_single: Decimal = Decimal("200000")
    additional_medicare_threshold_married: Decimal = Decimal("250000")
    additional_medicare_rate: Decimal = Decimal("0.009")
    
    # NIIT (Net Investment Income Tax)
    # Note: NIIT thresholds are NOT inflation-adjusted (set by ACA, IRC §1411)
    niit_threshold_single: Decimal = Decimal("200000")
    niit_threshold_married: Decimal = Decimal("250000")
    niit_threshold_married_separately: Decimal = Decimal("125000")
    niit_rate: Decimal = Decimal("0.038")

    # Additional Medicare tax thresholds
    # MFS threshold is $125,000 (IRC §3101(b)(2)); not inflation-adjusted
    additional_medicare_threshold_married_separately: Decimal = Decimal("125000")

    # AMT
    amt_exemption_single: Decimal = Decimal("88100")
    amt_exemption_married_jointly: Decimal = Decimal("137000")
    amt_phaseout_start_single: Decimal = Decimal("626350")
    amt_phaseout_start_married: Decimal = Decimal("1252700")
    amt_rate_low: Decimal = Decimal("0.26")
    amt_rate_high: Decimal = Decimal("0.28")
    # AMT 28% rate threshold: $239,100 for 2025 (Rev. Proc. 2024-40, §3.02)
    amt_rate_threshold: Decimal = Decimal("239100")
    
    # ---- Above-the-line deduction limits (2025) ----
    limit_401k: Decimal = Decimal("23500")
    limit_401k_catchup: Decimal = Decimal("7500")      # age 50+
    limit_ira: Decimal = Decimal("7000")
    limit_ira_catchup: Decimal = Decimal("1000")        # age 50+
    limit_hsa_single: Decimal = Decimal("4300")
    limit_hsa_family: Decimal = Decimal("8550")
    limit_student_loan_interest: Decimal = Decimal("2500")

    # Student loan interest phase-out (MAGI)
    student_loan_phaseout_start_single: Decimal = Decimal("80000")
    student_loan_phaseout_end_single: Decimal = Decimal("95000")
    student_loan_phaseout_start_mfj: Decimal = Decimal("165000")
    student_loan_phaseout_end_mfj: Decimal = Decimal("195000")

    # ---- Itemized deduction limits (2025) ----
    salt_cap_general: Decimal = Decimal("10000")        # Single/MFJ/HOH
    salt_cap_mfs: Decimal = Decimal("5000")             # Married Filing Separately
    mortgage_loan_limit: Decimal = Decimal("750000")    # Post-2017 mortgage limit
    medical_expense_floor_pct: Decimal = Decimal("0.075")  # 7.5% of AGI

    # ---- Child Tax Credit (2025) ----
    ctc_per_child: Decimal = Decimal("2000")
    ctc_refundable_per_child: Decimal = Decimal("1700")  # ACTC max per child
    other_dependent_credit_amount: Decimal = Decimal("500")
    ctc_phaseout_start_single: Decimal = Decimal("200000")
    ctc_phaseout_start_mfj: Decimal = Decimal("400000")
    ctc_phaseout_rate: Decimal = Decimal("50")           # $50 per $1,000 over threshold

    # ---- EITC (2025) ----
    eitc_investment_income_limit: Decimal = Decimal("11600")

    # ---- Education Credits (2025) ----
    aotc_max_credit: Decimal = Decimal("2500")
    aotc_refundable_pct: Decimal = Decimal("0.40")       # 40% of AOTC is refundable
    aotc_refundable_max: Decimal = Decimal("1000")
    aotc_phaseout_start_single: Decimal = Decimal("80000")
    aotc_phaseout_end_single: Decimal = Decimal("90000")
    aotc_phaseout_start_mfj: Decimal = Decimal("160000")
    aotc_phaseout_end_mfj: Decimal = Decimal("180000")

    llc_max_credit: Decimal = Decimal("2000")
    llc_phaseout_start_single: Decimal = Decimal("80000")
    llc_phaseout_end_single: Decimal = Decimal("90000")
    llc_phaseout_start_mfj: Decimal = Decimal("160000")
    llc_phaseout_end_mfj: Decimal = Decimal("180000")

    def get_standard_deduction(self, status: FilingStatus) -> Decimal:
        """Get standard deduction for filing status."""
        mapping = {
            FilingStatus.SINGLE: self.standard_deduction_single,
            FilingStatus.MARRIED_JOINTLY: self.standard_deduction_married_jointly,
            FilingStatus.MARRIED_SEPARATELY: self.standard_deduction_married_separately,
            FilingStatus.HEAD_OF_HOUSEHOLD: self.standard_deduction_head_of_household,
        }
        return mapping[status]


# Federal tax brackets for 2025
FEDERAL_BRACKETS_2025 = {
    FilingStatus.SINGLE: [
        (Decimal("11925"), Decimal("0.10")),
        (Decimal("48475"), Decimal("0.12")),
        (Decimal("103350"), Decimal("0.22")),
        (Decimal("197300"), Decimal("0.24")),
        (Decimal("250525"), Decimal("0.32")),
        (Decimal("626350"), Decimal("0.35")),
        (Decimal("Infinity"), Decimal("0.37")),
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (Decimal("23850"), Decimal("0.10")),
        (Decimal("96950"), Decimal("0.12")),
        (Decimal("206700"), Decimal("0.22")),
        (Decimal("394600"), Decimal("0.24")),
        (Decimal("501050"), Decimal("0.32")),
        (Decimal("751600"), Decimal("0.35")),
        (Decimal("Infinity"), Decimal("0.37")),
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (Decimal("11925"), Decimal("0.10")),
        (Decimal("48475"), Decimal("0.12")),
        (Decimal("103350"), Decimal("0.22")),
        (Decimal("197300"), Decimal("0.24")),
        (Decimal("250525"), Decimal("0.32")),
        (Decimal("375800"), Decimal("0.35")),
        (Decimal("Infinity"), Decimal("0.37")),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (Decimal("17000"), Decimal("0.10")),
        (Decimal("64850"), Decimal("0.12")),
        (Decimal("103350"), Decimal("0.22")),
        (Decimal("197300"), Decimal("0.24")),
        (Decimal("250500"), Decimal("0.32")),
        (Decimal("626350"), Decimal("0.35")),
        (Decimal("Infinity"), Decimal("0.37")),
    ],
}

# Long-term capital gains brackets for 2025
# Source: Rev. Proc. 2024-40; Tax Foundation Table 6.
LTCG_BRACKETS_2025 = {
    FilingStatus.SINGLE: [
        (Decimal("48350"), Decimal("0.00")),
        (Decimal("533400"), Decimal("0.15")),
        (Decimal("Infinity"), Decimal("0.20")),
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (Decimal("96700"), Decimal("0.00")),
        (Decimal("600050"), Decimal("0.15")),
        (Decimal("Infinity"), Decimal("0.20")),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (Decimal("64750"), Decimal("0.00")),
        (Decimal("566700"), Decimal("0.15")),
        (Decimal("Infinity"), Decimal("0.20")),
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (Decimal("48350"), Decimal("0.00")),
        (Decimal("300000"), Decimal("0.15")),
        (Decimal("Infinity"), Decimal("0.20")),
    ],
}


class EquityGrant(BaseModel):
    """Represents an equity grant (RSU, ISO, NSO, ESPP)."""
    type: EquityType
    company: str
    grant_date: str  # ISO date string
    shares: Decimal
    grant_price: Decimal  # Price at grant (for options)
    vested_shares: Decimal = Decimal("0")
    exercised_shares: Decimal = Decimal("0")
    sold_shares: Decimal = Decimal("0")


class IncomeBreakdown(BaseModel):
    """Breakdown of different income types."""
    w2_wages: Decimal = Decimal("0")
    rsu_income: Decimal = Decimal("0")  # Ordinary income from RSU vesting
    nso_income: Decimal = Decimal("0")  # Ordinary income from NSO exercise
    short_term_gains: Decimal = Decimal("0")  # < 1 year holding
    long_term_gains: Decimal = Decimal("0")  # >= 1 year holding
    qualified_dividends: Decimal = Decimal("0")
    interest_income: Decimal = Decimal("0")
    iso_bargain_element: Decimal = Decimal("0")  # For AMT only
    
    @property
    def ordinary_income(self) -> Decimal:
        """Total ordinary income (taxed at regular rates)."""
        return (
            self.w2_wages +
            self.rsu_income +
            self.nso_income +
            self.short_term_gains +
            self.interest_income
        )
    
    @property
    def preferential_income(self) -> Decimal:
        """Total preferential income (LTCG/QDIV rates)."""
        return self.long_term_gains + self.qualified_dividends
    
    @property
    def total_income(self) -> Decimal:
        """Total gross income."""
        return self.ordinary_income + self.preferential_income


class ItemizedDeductionsDetail(BaseModel):
    """Breakdown of itemized deductions components."""
    mortgage_interest: Decimal = Decimal("0")
    salt: Decimal = Decimal("0")            # After cap
    salt_paid: Decimal = Decimal("0")       # Before cap (for reference)
    charitable: Decimal = Decimal("0")
    medical: Decimal = Decimal("0")         # After 7.5% AGI floor
    medical_paid: Decimal = Decimal("0")    # Before floor (for reference)
    total: Decimal = Decimal("0")


class AboveTheLineDeductionsDetail(BaseModel):
    """Breakdown of above-the-line (AGI) deductions."""
    contributions_401k: Decimal = Decimal("0")
    ira_contributions: Decimal = Decimal("0")
    hsa_contributions: Decimal = Decimal("0")
    student_loan_interest: Decimal = Decimal("0")
    total: Decimal = Decimal("0")


class TaxSummary(BaseModel):
    """Complete tax calculation summary."""
    year: int = 2025
    filing_status: FilingStatus

    # Income
    income: IncomeBreakdown

    # Above-the-line deductions (AGI adjustments)
    above_the_line_deductions: AboveTheLineDeductionsDetail = Field(
        default_factory=AboveTheLineDeductionsDetail
    )
    agi: Decimal = Decimal("0")  # Adjusted Gross Income

    # Deductions
    standard_deduction: Decimal = Decimal("0")
    itemized_deductions: Decimal = Decimal("0")         # total itemized (pre-computed or computed)
    itemized_deductions_detail: ItemizedDeductionsDetail = Field(
        default_factory=ItemizedDeductionsDetail
    )
    deduction_used: Decimal = Decimal("0")              # max(standard, itemized)

    # Taxable income
    taxable_income: Decimal = Decimal("0")

    # Federal tax (before credits)
    federal_tax_on_ordinary: Decimal = Decimal("0")
    federal_tax_on_ltcg: Decimal = Decimal("0")
    federal_tax_total: Decimal = Decimal("0")           # includes AMT, before credits

    # AMT
    amt_income: Decimal = Decimal("0")
    tentative_minimum_tax: Decimal = Decimal("0")
    amt_owed: Decimal = Decimal("0")                    # max(0, TMT - regular tax)

    # FICA
    social_security_tax: Decimal = Decimal("0")
    medicare_tax: Decimal = Decimal("0")
    additional_medicare_tax: Decimal = Decimal("0")
    niit: Decimal = Decimal("0")                        # Net Investment Income Tax

    # Credits
    child_tax_credit: Decimal = Decimal("0")            # Non-refundable CTC
    other_dependent_credit: Decimal = Decimal("0")      # $500/dependent non-CTC
    actc: Decimal = Decimal("0")                        # Additional CTC (refundable)
    eitc: Decimal = Decimal("0")                        # Earned Income Credit (refundable)
    education_credit: Decimal = Decimal("0")            # AOTC/LLC non-refundable portion
    education_credit_refundable: Decimal = Decimal("0") # AOTC refundable portion
    total_credits: Decimal = Decimal("0")               # All credits combined

    # State (CA)
    state_tax: Decimal = Decimal("0")
    state_code: Optional[str] = None

    # Totals
    total_tax: Decimal = Decimal("0")
    effective_rate: Decimal = Decimal("0")
    marginal_rate: Decimal = Decimal("0")

    # Withholding comparison
    total_withheld: Decimal = Decimal("0")
    balance_due: Decimal = Decimal("0")  # positive = owe, negative = refund

    # Warnings
    warnings: list[str] = Field(default_factory=list)
