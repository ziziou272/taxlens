"""
Manual Entry Data Models for TaxLens.

Provides structured data models for manual input of:
- W-2 income data
- Equity grants and vesting schedules
- Stock transactions
- Other income sources
- Withholdings

All monetary values use Decimal for exact arithmetic.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EquityAwardType(str, Enum):
    """Types of equity awards."""
    RSU = "rsu"
    ISO = "iso"
    NSO = "nso"
    ESPP = "espp"


class HoldingPeriod(str, Enum):
    """Holding period for capital gains."""
    SHORT_TERM = "short_term"  # <= 1 year
    LONG_TERM = "long_term"    # > 1 year


class IncomeType(str, Enum):
    """Types of other income."""
    INTEREST = "interest"
    DIVIDEND_QUALIFIED = "dividend_qualified"
    DIVIDEND_ORDINARY = "dividend_ordinary"
    RENTAL = "rental"
    BUSINESS = "business"
    CAPITAL_GAIN = "capital_gain"
    OTHER = "other"


# ===========================================================
# W-2 Income Entry
# ===========================================================

class W2Entry(BaseModel):
    """
    W-2 income entry for an employer.
    
    Maps to IRS Form W-2 boxes.
    """
    employer_name: str
    employer_ein: Optional[str] = None
    tax_year: int = 2025
    
    # Box 1: Wages, tips, other compensation
    wages: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Box 2: Federal income tax withheld
    federal_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Box 3: Social Security wages
    social_security_wages: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Box 4: Social Security tax withheld
    social_security_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Box 5: Medicare wages and tips
    medicare_wages: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Box 6: Medicare tax withheld
    medicare_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Box 12 codes (common ones for equity)
    box_12_codes: dict[str, Decimal] = Field(default_factory=dict)
    # Common codes:
    # V = Income from NSO exercise
    # D = 401(k) elective deferrals
    # E = 403(b) elective deferrals
    # W = HSA contributions
    
    # State withholding
    state_code: Optional[str] = None
    state_wages: Decimal = Field(default=Decimal("0"), ge=0)
    state_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Local withholding
    local_wages: Decimal = Field(default=Decimal("0"), ge=0)
    local_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Additional notes
    notes: Optional[str] = None
    
    @property
    def total_withheld(self) -> Decimal:
        """Total tax withheld from W-2."""
        return (
            self.federal_withheld +
            self.social_security_withheld +
            self.medicare_withheld +
            self.state_withheld +
            self.local_withheld
        )
    
    @property
    def nso_income(self) -> Decimal:
        """NSO exercise income from Box 12 Code V."""
        return self.box_12_codes.get("V", Decimal("0"))


# ===========================================================
# Equity Grant Entry
# ===========================================================

class EquityGrantEntry(BaseModel):
    """
    Equity grant (RSU/ISO/NSO/ESPP) entry.
    """
    award_type: EquityAwardType
    company: str
    symbol: Optional[str] = None
    
    # Grant details
    grant_date: date
    grant_id: Optional[str] = None  # Company's grant identifier
    
    # Share counts
    shares_granted: Decimal = Field(default=Decimal("0"), ge=0)
    shares_vested: Decimal = Field(default=Decimal("0"), ge=0)
    shares_exercised: Decimal = Field(default=Decimal("0"), ge=0)
    shares_sold: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Prices (for options)
    grant_price: Decimal = Field(default=Decimal("0"), ge=0)  # Strike price for ISO/NSO
    
    # Vesting schedule
    vesting_start_date: Optional[date] = None
    vesting_schedule: Optional[str] = None  # e.g., "4 years monthly with 1 year cliff"
    
    # ESPP specific
    offering_period_start: Optional[date] = None
    offering_period_end: Optional[date] = None
    lookback_provision: bool = False
    
    notes: Optional[str] = None
    
    @property
    def shares_remaining(self) -> Decimal:
        """Unvested shares remaining."""
        return self.shares_granted - self.shares_vested
    
    @property
    def shares_exercisable(self) -> Decimal:
        """Shares vested but not yet exercised (for ISO/NSO)."""
        if self.award_type in (EquityAwardType.ISO, EquityAwardType.NSO):
            return self.shares_vested - self.shares_exercised
        return Decimal("0")


class VestingEventEntry(BaseModel):
    """
    Record of a vesting event.
    """
    grant_id: Optional[str] = None
    vest_date: date
    shares_vested: Decimal = Field(ge=0)
    fmv_at_vest: Decimal = Field(ge=0)  # Fair Market Value per share
    
    # Withholding
    shares_withheld_for_taxes: Decimal = Field(default=Decimal("0"), ge=0)
    federal_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    state_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    fica_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    @property
    def shares_net(self) -> Decimal:
        """Shares received after withholding."""
        return self.shares_vested - self.shares_withheld_for_taxes
    
    @property
    def gross_income(self) -> Decimal:
        """Ordinary income recognized (all shares vested)."""
        return self.shares_vested * self.fmv_at_vest
    
    @property
    def total_withheld(self) -> Decimal:
        """Total tax withheld at vesting."""
        return self.federal_withheld + self.state_withheld + self.fica_withheld


class OptionExerciseEntry(BaseModel):
    """
    Record of an ISO or NSO exercise event.
    """
    exercise_date: date
    award_type: EquityAwardType  # ISO or NSO
    grant_id: Optional[str] = None
    grant_date: Optional[date] = None
    
    shares_exercised: Decimal = Field(ge=0)
    strike_price: Decimal = Field(ge=0)  # Exercise price per share
    fmv_at_exercise: Decimal = Field(ge=0)  # FMV at time of exercise
    
    # For NSO: ordinary income is recognized at exercise
    # For ISO: no ordinary income, but AMT preference item
    
    # Whether shares were held or sold
    same_day_sale: bool = False
    
    # Withholding (NSO only typically)
    federal_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    state_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    @property
    def bargain_element(self) -> Decimal:
        """Bargain element (FMV - strike price) per share."""
        return self.fmv_at_exercise - self.strike_price
    
    @property
    def total_bargain_element(self) -> Decimal:
        """Total bargain element for all shares."""
        return self.bargain_element * self.shares_exercised
    
    @property
    def exercise_cost(self) -> Decimal:
        """Total cost to exercise options."""
        return self.strike_price * self.shares_exercised
    
    @property
    def nso_ordinary_income(self) -> Decimal:
        """Ordinary income for NSO exercise."""
        if self.award_type == EquityAwardType.NSO:
            return self.total_bargain_element
        return Decimal("0")
    
    @property
    def iso_amt_preference(self) -> Decimal:
        """AMT preference item for ISO exercise (if held)."""
        if self.award_type == EquityAwardType.ISO and not self.same_day_sale:
            return self.total_bargain_element
        return Decimal("0")


# ===========================================================
# Stock Sale Entry
# ===========================================================

class StockSaleEntry(BaseModel):
    """
    Record of a stock sale.
    """
    sale_date: date
    symbol: str
    company: Optional[str] = None
    
    shares_sold: Decimal = Field(ge=0)
    sale_price: Decimal = Field(ge=0)  # Per share
    
    # Cost basis
    acquisition_date: date
    cost_basis_per_share: Decimal = Field(ge=0)
    
    # Fees
    commission: Decimal = Field(default=Decimal("0"), ge=0)
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Source of shares
    source: Optional[EquityAwardType] = None  # RSU, ISO, NSO, ESPP, or None for purchased
    grant_id: Optional[str] = None
    
    # For ESPP/ISO - track for qualified vs disqualifying disposition
    is_qualifying_disposition: Optional[bool] = None
    
    notes: Optional[str] = None
    
    @property
    def gross_proceeds(self) -> Decimal:
        """Gross sale proceeds."""
        return self.shares_sold * self.sale_price
    
    @property
    def net_proceeds(self) -> Decimal:
        """Net proceeds after fees."""
        return self.gross_proceeds - self.commission - self.fees
    
    @property
    def total_cost_basis(self) -> Decimal:
        """Total cost basis for shares sold."""
        return self.shares_sold * self.cost_basis_per_share
    
    @property
    def gain_loss(self) -> Decimal:
        """Capital gain or loss."""
        return self.net_proceeds - self.total_cost_basis
    
    @property
    def holding_period(self) -> HoldingPeriod:
        """Determine if short or long term."""
        days_held = (self.sale_date - self.acquisition_date).days
        if days_held > 365:
            return HoldingPeriod.LONG_TERM
        return HoldingPeriod.SHORT_TERM
    
    @property
    def days_held(self) -> int:
        """Number of days shares were held."""
        return (self.sale_date - self.acquisition_date).days


# ===========================================================
# Other Income Entry
# ===========================================================

class OtherIncomeEntry(BaseModel):
    """
    Entry for other types of income.
    """
    income_type: IncomeType
    description: str
    tax_year: int = 2025
    
    amount: Decimal
    date_received: Optional[date] = None
    
    # Payer information
    payer_name: Optional[str] = None
    payer_ein: Optional[str] = None
    
    # Withholding
    federal_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    state_withheld: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Form reference
    form_type: Optional[str] = None  # 1099-INT, 1099-DIV, 1099-B, etc.
    
    notes: Optional[str] = None


# ===========================================================
# Estimated Tax Payment Entry
# ===========================================================

class EstimatedPaymentEntry(BaseModel):
    """
    Record of an estimated tax payment.
    """
    payment_date: date
    tax_year: int = 2025
    quarter: int = Field(ge=1, le=4)  # Q1-Q4
    
    federal_amount: Decimal = Field(default=Decimal("0"), ge=0)
    state_amount: Decimal = Field(default=Decimal("0"), ge=0)
    state_code: Optional[str] = None
    
    # Payment method
    payment_method: Optional[str] = None  # EFTPS, Check, Direct Pay, etc.
    confirmation_number: Optional[str] = None
    
    notes: Optional[str] = None
    
    @property
    def total_amount(self) -> Decimal:
        """Total estimated payment."""
        return self.federal_amount + self.state_amount


# ===========================================================
# Tax Profile (combines all entries)
# ===========================================================

class TaxProfile(BaseModel):
    """
    Complete tax profile combining all manual entries.
    """
    tax_year: int = 2025
    
    # Personal info
    filing_status: str = "single"  # single, married_jointly, etc.
    state_of_residence: str = "CA"
    
    # Income entries
    w2_entries: list[W2Entry] = Field(default_factory=list)
    equity_grants: list[EquityGrantEntry] = Field(default_factory=list)
    vesting_events: list[VestingEventEntry] = Field(default_factory=list)
    option_exercises: list[OptionExerciseEntry] = Field(default_factory=list)
    stock_sales: list[StockSaleEntry] = Field(default_factory=list)
    other_income: list[OtherIncomeEntry] = Field(default_factory=list)
    
    # Payments
    estimated_payments: list[EstimatedPaymentEntry] = Field(default_factory=list)
    
    # Deductions (simplified)
    itemized_deductions: Decimal = Field(default=Decimal("0"), ge=0)
    use_standard_deduction: bool = True
    
    # Prior year info (for safe harbor)
    prior_year_tax: Optional[Decimal] = None
    prior_year_agi: Optional[Decimal] = None
    
    @property
    def total_w2_wages(self) -> Decimal:
        """Sum of all W-2 wages."""
        return sum(w2.wages for w2 in self.w2_entries)
    
    @property
    def total_federal_withheld(self) -> Decimal:
        """Sum of all federal withholding."""
        w2_withheld = sum(w2.federal_withheld for w2 in self.w2_entries)
        vest_withheld = sum(v.federal_withheld for v in self.vesting_events)
        exercise_withheld = sum(e.federal_withheld for e in self.option_exercises)
        other_withheld = sum(o.federal_withheld for o in self.other_income)
        return w2_withheld + vest_withheld + exercise_withheld + other_withheld
    
    @property
    def total_state_withheld(self) -> Decimal:
        """Sum of all state withholding."""
        w2_withheld = sum(w2.state_withheld for w2 in self.w2_entries)
        vest_withheld = sum(v.state_withheld for v in self.vesting_events)
        exercise_withheld = sum(e.state_withheld for e in self.option_exercises)
        other_withheld = sum(o.state_withheld for o in self.other_income)
        return w2_withheld + vest_withheld + exercise_withheld + other_withheld
    
    @property
    def total_estimated_payments_federal(self) -> Decimal:
        """Sum of federal estimated payments."""
        return sum(ep.federal_amount for ep in self.estimated_payments)
    
    @property
    def total_estimated_payments_state(self) -> Decimal:
        """Sum of state estimated payments."""
        return sum(ep.state_amount for ep in self.estimated_payments)
    
    @property
    def total_rsu_income(self) -> Decimal:
        """Sum of RSU vesting income."""
        return sum(
            v.gross_income for v in self.vesting_events
            # Note: Need to track grant type to filter RSU only
        )
    
    @property
    def total_nso_income(self) -> Decimal:
        """Sum of NSO exercise income."""
        return sum(
            e.nso_ordinary_income for e in self.option_exercises
            if e.award_type == EquityAwardType.NSO
        )
    
    @property
    def total_iso_amt_preference(self) -> Decimal:
        """Sum of ISO AMT preference items."""
        return sum(
            e.iso_amt_preference for e in self.option_exercises
            if e.award_type == EquityAwardType.ISO
        )
    
    @property
    def total_short_term_gains(self) -> Decimal:
        """Sum of short-term capital gains."""
        return sum(
            s.gain_loss for s in self.stock_sales
            if s.holding_period == HoldingPeriod.SHORT_TERM
        )
    
    @property
    def total_long_term_gains(self) -> Decimal:
        """Sum of long-term capital gains."""
        return sum(
            s.gain_loss for s in self.stock_sales
            if s.holding_period == HoldingPeriod.LONG_TERM
        )
    
    @property
    def total_qualified_dividends(self) -> Decimal:
        """Sum of qualified dividends."""
        return sum(
            o.amount for o in self.other_income
            if o.income_type == IncomeType.DIVIDEND_QUALIFIED
        )
    
    @property
    def total_interest_income(self) -> Decimal:
        """Sum of interest income."""
        return sum(
            o.amount for o in self.other_income
            if o.income_type == IncomeType.INTEREST
        )


# ===========================================================
# Helper Functions
# ===========================================================

def create_w2_from_dict(data: dict) -> W2Entry:
    """Create W2Entry from dictionary."""
    # Convert numeric fields to Decimal
    for field_name in [
        "wages", "federal_withheld", "social_security_wages",
        "social_security_withheld", "medicare_wages", "medicare_withheld",
        "state_wages", "state_withheld", "local_wages", "local_withheld"
    ]:
        if field_name in data and not isinstance(data[field_name], Decimal):
            data[field_name] = Decimal(str(data[field_name]))
    
    # Convert box_12_codes values to Decimal
    if "box_12_codes" in data:
        data["box_12_codes"] = {
            k: Decimal(str(v)) for k, v in data["box_12_codes"].items()
        }
    
    return W2Entry(**data)


def create_stock_sale_from_dict(data: dict) -> StockSaleEntry:
    """Create StockSaleEntry from dictionary."""
    # Convert numeric fields to Decimal
    for field_name in [
        "shares_sold", "sale_price", "cost_basis_per_share",
        "commission", "fees"
    ]:
        if field_name in data and not isinstance(data[field_name], Decimal):
            data[field_name] = Decimal(str(data[field_name]))
    
    # Convert date strings to date objects
    for date_field in ["sale_date", "acquisition_date"]:
        if date_field in data and isinstance(data[date_field], str):
            from datetime import datetime
            data[date_field] = datetime.strptime(data[date_field], "%Y-%m-%d").date()
    
    return StockSaleEntry(**data)


def merge_tax_profiles(profiles: list[TaxProfile]) -> TaxProfile:
    """
    Merge multiple tax profiles into one.
    
    Useful for combining imported data with manual entries.
    """
    if not profiles:
        return TaxProfile()
    
    merged = TaxProfile(
        tax_year=profiles[0].tax_year,
        filing_status=profiles[0].filing_status,
        state_of_residence=profiles[0].state_of_residence,
    )
    
    for profile in profiles:
        merged.w2_entries.extend(profile.w2_entries)
        merged.equity_grants.extend(profile.equity_grants)
        merged.vesting_events.extend(profile.vesting_events)
        merged.option_exercises.extend(profile.option_exercises)
        merged.stock_sales.extend(profile.stock_sales)
        merged.other_income.extend(profile.other_income)
        merged.estimated_payments.extend(profile.estimated_payments)
    
    # Use larger deduction
    merged.itemized_deductions = max(p.itemized_deductions for p in profiles)
    
    # Use prior year info from first profile that has it
    for profile in profiles:
        if profile.prior_year_tax is not None:
            merged.prior_year_tax = profile.prior_year_tax
            merged.prior_year_agi = profile.prior_year_agi
            break
    
    return merged
