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
    niit_threshold_single: Decimal = Decimal("200000")
    niit_threshold_married: Decimal = Decimal("250000")
    niit_rate: Decimal = Decimal("0.038")
    
    # AMT
    amt_exemption_single: Decimal = Decimal("88100")
    amt_exemption_married_jointly: Decimal = Decimal("137000")
    amt_phaseout_start_single: Decimal = Decimal("626350")
    amt_phaseout_start_married: Decimal = Decimal("1252700")
    amt_rate_low: Decimal = Decimal("0.26")
    amt_rate_high: Decimal = Decimal("0.28")
    amt_rate_threshold: Decimal = Decimal("232600")
    
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


class TaxSummary(BaseModel):
    """Complete tax calculation summary."""
    year: int = 2025
    filing_status: FilingStatus
    
    # Income
    income: IncomeBreakdown
    
    # Deductions
    standard_deduction: Decimal = Decimal("0")
    itemized_deductions: Decimal = Decimal("0")
    deduction_used: Decimal = Decimal("0")  # max(standard, itemized)
    
    # Taxable income
    taxable_income: Decimal = Decimal("0")
    
    # Federal tax
    federal_tax_on_ordinary: Decimal = Decimal("0")
    federal_tax_on_ltcg: Decimal = Decimal("0")
    federal_tax_total: Decimal = Decimal("0")
    
    # AMT
    amt_income: Decimal = Decimal("0")
    tentative_minimum_tax: Decimal = Decimal("0")
    amt_owed: Decimal = Decimal("0")  # max(0, TMT - regular tax)
    
    # FICA
    social_security_tax: Decimal = Decimal("0")
    medicare_tax: Decimal = Decimal("0")
    additional_medicare_tax: Decimal = Decimal("0")
    niit: Decimal = Decimal("0")  # Net Investment Income Tax
    
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
