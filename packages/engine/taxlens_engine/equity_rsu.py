"""
RSU (Restricted Stock Units) calculations for TaxLens.

RSUs are the simplest form of equity compensation:
- At vesting: FMV is ordinary income (W-2), subject to withholding
- At sale: Gain/loss from FMV at vest is capital gain/loss

Key characteristics:
- No purchase price (unlike ISO/NSO)
- Taxed as ordinary income at vesting
- Cost basis = FMV at vesting date
- Holding period starts at vesting

Withholding rates (supplemental income):
- Federal: 22% (or 37% if >$1M)
- CA: 10.23%
- Social Security: 6.2% (up to wage base)
- Medicare: 1.45% (+ 0.9% additional over threshold)
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Optional


# Supplemental withholding rates (2025)
FEDERAL_SUPPLEMENTAL_RATE = Decimal("0.22")  # 22% for < $1M
FEDERAL_SUPPLEMENTAL_RATE_HIGH = Decimal("0.37")  # 37% for > $1M
FEDERAL_HIGH_INCOME_THRESHOLD = Decimal("1000000")  # $1M threshold

CA_SUPPLEMENTAL_RATE = Decimal("0.1023")  # 10.23%

SOCIAL_SECURITY_RATE = Decimal("0.062")  # 6.2%
SOCIAL_SECURITY_WAGE_BASE = Decimal("176100")  # 2025

MEDICARE_RATE = Decimal("0.0145")  # 1.45%
ADDITIONAL_MEDICARE_RATE = Decimal("0.009")  # 0.9%
ADDITIONAL_MEDICARE_THRESHOLD_SINGLE = Decimal("200000")
ADDITIONAL_MEDICARE_THRESHOLD_MARRIED = Decimal("250000")


@dataclass
class RSUGrant:
    """
    Represents an RSU grant.
    
    RSUs vest over time according to a vesting schedule.
    At vesting, shares become yours and are taxed as ordinary income.
    """
    grant_date: date
    total_shares: Decimal
    company: str = ""
    vesting_schedule: Optional[str] = None  # e.g., "4 years with 1 year cliff"
    
    def shares_remaining(
        self,
        shares_vested: Decimal = Decimal("0"),
    ) -> Decimal:
        """Calculate unvested shares."""
        return max(Decimal("0"), self.total_shares - shares_vested)


@dataclass
class RSUVesting:
    """
    Represents an RSU vesting event.
    
    At vesting:
    - Shares become yours
    - FMV × shares = ordinary income (W-2)
    - Employer withholds taxes (often by selling some shares)
    """
    vesting_date: date
    shares_vested: Decimal
    fmv_at_vesting: Decimal  # Fair Market Value per share
    shares_withheld_for_taxes: Decimal = Decimal("0")  # Shares sold for tax withholding
    grant_date: Optional[date] = None  # Original grant date
    
    @property
    def gross_income(self) -> Decimal:
        """
        Gross ordinary income from vesting.
        
        This is W-2 income = FMV × shares vested.
        """
        return (self.shares_vested * self.fmv_at_vesting).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def cost_basis_per_share(self) -> Decimal:
        """Cost basis per share = FMV at vesting."""
        return self.fmv_at_vesting
    
    @property
    def total_cost_basis(self) -> Decimal:
        """Total cost basis for all vested shares."""
        return (self.shares_vested * self.fmv_at_vesting).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def net_shares(self) -> Decimal:
        """Shares remaining after tax withholding."""
        return self.shares_vested - self.shares_withheld_for_taxes


@dataclass
class RSUWithholding:
    """
    Breakdown of tax withholding on RSU vesting.
    
    Employers typically withhold:
    - Federal income tax (supplemental rate)
    - State income tax
    - Social Security (up to wage base)
    - Medicare
    """
    gross_income: Decimal
    federal_withholding: Decimal
    state_withholding: Decimal
    social_security: Decimal
    medicare: Decimal
    additional_medicare: Decimal = Decimal("0")
    
    @property
    def total_withholding(self) -> Decimal:
        """Total tax withholding."""
        return (
            self.federal_withholding +
            self.state_withholding +
            self.social_security +
            self.medicare +
            self.additional_medicare
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property
    def net_value(self) -> Decimal:
        """Net value after all withholding."""
        return (self.gross_income - self.total_withholding).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def effective_withholding_rate(self) -> Decimal:
        """Effective total withholding rate."""
        if self.gross_income <= 0:
            return Decimal("0")
        return (self.total_withholding / self.gross_income).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )


@dataclass  
class RSUSale:
    """
    Represents selling RSU shares.
    
    Capital gain/loss = (Sale Price - FMV at Vest) × Shares
    """
    sale_date: date
    shares_sold: Decimal
    sale_price: Decimal
    cost_basis_per_share: Decimal  # FMV at vesting
    vesting_date: date  # For holding period calculation
    
    @property
    def proceeds(self) -> Decimal:
        """Total sale proceeds."""
        return (self.shares_sold * self.sale_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def total_cost_basis(self) -> Decimal:
        """Total cost basis."""
        return (self.shares_sold * self.cost_basis_per_share).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def capital_gain(self) -> Decimal:
        """
        Capital gain (or loss if negative).
        
        This is the gain/loss from sale price vs FMV at vesting.
        """
        return (self.proceeds - self.total_cost_basis).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def holding_period_days(self) -> int:
        """Days held since vesting."""
        return (self.sale_date - self.vesting_date).days
    
    @property
    def is_long_term(self) -> bool:
        """
        Is this a long-term capital gain?
        
        Long-term = held > 1 year from vesting date.
        """
        return self.holding_period_days > 365
    
    @property
    def gain_type(self) -> str:
        """Return 'long_term' or 'short_term'."""
        return "long_term" if self.is_long_term else "short_term"


def calculate_rsu_withholding(
    gross_income: Decimal,
    state: str = "CA",
    ytd_wages: Decimal = Decimal("0"),
    filing_status: str = "single",
) -> RSUWithholding:
    """
    Calculate estimated tax withholding on RSU vesting.
    
    Uses supplemental withholding rates (flat rates for bonus/RSU).
    
    Args:
        gross_income: RSU vesting value (FMV × shares)
        state: Two-letter state code (currently only CA supported)
        ytd_wages: Year-to-date wages (for SS wage base check)
        filing_status: "single" or "married" (for additional Medicare)
        
    Returns:
        RSUWithholding breakdown
    """
    # Federal withholding (supplemental rate)
    if gross_income > FEDERAL_HIGH_INCOME_THRESHOLD:
        federal = gross_income * FEDERAL_SUPPLEMENTAL_RATE_HIGH
    else:
        federal = gross_income * FEDERAL_SUPPLEMENTAL_RATE
    
    # State withholding
    if state.upper() == "CA":
        state_tax = gross_income * CA_SUPPLEMENTAL_RATE
    else:
        # Default to 5% for other states (rough estimate)
        state_tax = gross_income * Decimal("0.05")
    
    # Social Security (6.2% up to wage base)
    ss_room = max(Decimal("0"), SOCIAL_SECURITY_WAGE_BASE - ytd_wages)
    ss_taxable = min(gross_income, ss_room)
    social_security = ss_taxable * SOCIAL_SECURITY_RATE
    
    # Medicare (1.45% on all income)
    medicare = gross_income * MEDICARE_RATE
    
    # Additional Medicare (0.9% over threshold)
    if filing_status == "married":
        medicare_threshold = ADDITIONAL_MEDICARE_THRESHOLD_MARRIED
    else:
        medicare_threshold = ADDITIONAL_MEDICARE_THRESHOLD_SINGLE
    
    # Check if this vesting pushes over the threshold
    total_wages = ytd_wages + gross_income
    if total_wages > medicare_threshold:
        # Calculate additional Medicare on amount over threshold
        taxable_for_additional = min(
            gross_income,
            total_wages - medicare_threshold
        )
        additional_medicare = max(
            Decimal("0"),
            taxable_for_additional * ADDITIONAL_MEDICARE_RATE
        )
    else:
        additional_medicare = Decimal("0")
    
    return RSUWithholding(
        gross_income=gross_income,
        federal_withholding=federal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        state_withholding=state_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        social_security=social_security.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        medicare=medicare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        additional_medicare=additional_medicare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )


def calculate_rsu_vesting(
    shares: Decimal,
    fmv: Decimal,
    vesting_date: date,
    state: str = "CA",
    ytd_wages: Decimal = Decimal("0"),
    filing_status: str = "single",
    grant_date: Optional[date] = None,
) -> dict:
    """
    Calculate complete RSU vesting event with withholding.
    
    Args:
        shares: Number of shares vesting
        fmv: Fair market value per share at vesting
        vesting_date: Date of vesting
        state: Two-letter state code
        ytd_wages: Year-to-date wages before this vesting
        filing_status: "single" or "married"
        grant_date: Original grant date (optional)
        
    Returns:
        Dict with vesting details and withholding breakdown
    """
    vesting = RSUVesting(
        vesting_date=vesting_date,
        shares_vested=shares,
        fmv_at_vesting=fmv,
        grant_date=grant_date,
    )
    
    withholding = calculate_rsu_withholding(
        gross_income=vesting.gross_income,
        state=state,
        ytd_wages=ytd_wages,
        filing_status=filing_status,
    )
    
    # Calculate shares needed to cover withholding
    shares_for_taxes = (withholding.total_withholding / fmv).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    
    return {
        "vesting_date": str(vesting_date),
        "shares_vested": shares,
        "fmv_per_share": fmv,
        "gross_income": vesting.gross_income,
        "cost_basis_per_share": fmv,
        "withholding": {
            "federal": withholding.federal_withholding,
            "state": withholding.state_withholding,
            "social_security": withholding.social_security,
            "medicare": withholding.medicare,
            "additional_medicare": withholding.additional_medicare,
            "total": withholding.total_withholding,
        },
        "net_value": withholding.net_value,
        "effective_rate": withholding.effective_withholding_rate,
        "shares_for_taxes": shares_for_taxes,
        "net_shares": shares - shares_for_taxes,
    }


def calculate_rsu_sale(
    shares: Decimal,
    sale_price: Decimal,
    cost_basis_per_share: Decimal,
    sale_date: date,
    vesting_date: date,
) -> dict:
    """
    Calculate capital gain/loss from RSU sale.
    
    Args:
        shares: Number of shares sold
        sale_price: Sale price per share
        cost_basis_per_share: FMV at vesting (cost basis)
        sale_date: Date of sale
        vesting_date: Date shares vested (for holding period)
        
    Returns:
        Dict with sale details and tax implications
    """
    sale = RSUSale(
        sale_date=sale_date,
        shares_sold=shares,
        sale_price=sale_price,
        cost_basis_per_share=cost_basis_per_share,
        vesting_date=vesting_date,
    )
    
    return {
        "sale_date": str(sale_date),
        "shares_sold": shares,
        "sale_price": sale_price,
        "proceeds": sale.proceeds,
        "cost_basis_per_share": cost_basis_per_share,
        "total_cost_basis": sale.total_cost_basis,
        "capital_gain": sale.capital_gain,
        "holding_period_days": sale.holding_period_days,
        "is_long_term": sale.is_long_term,
        "gain_type": sale.gain_type,
    }


def analyze_rsu_scenario(
    shares: Decimal,
    fmv_at_vesting: Decimal,
    sale_price: Decimal,
    vesting_date: date,
    sale_date: date,
    state: str = "CA",
) -> dict:
    """
    Complete analysis of RSU vesting and sale.
    
    Args:
        shares: Number of shares
        fmv_at_vesting: FMV per share at vesting
        sale_price: Sale price per share
        vesting_date: Date of vesting
        sale_date: Date of sale
        state: State for withholding
        
    Returns:
        Complete analysis with tax breakdown
    """
    vesting = RSUVesting(
        vesting_date=vesting_date,
        shares_vested=shares,
        fmv_at_vesting=fmv_at_vesting,
    )
    
    sale = RSUSale(
        sale_date=sale_date,
        shares_sold=shares,
        sale_price=sale_price,
        cost_basis_per_share=fmv_at_vesting,
        vesting_date=vesting_date,
    )
    
    withholding = calculate_rsu_withholding(vesting.gross_income, state=state)
    
    return {
        "summary": {
            "shares": shares,
            "fmv_at_vesting": fmv_at_vesting,
            "sale_price": sale_price,
            "vesting_date": str(vesting_date),
            "sale_date": str(sale_date),
        },
        "at_vesting": {
            "ordinary_income": vesting.gross_income,
            "cost_basis": vesting.total_cost_basis,
            "withholding": withholding.total_withholding,
            "net_value": withholding.net_value,
        },
        "at_sale": {
            "proceeds": sale.proceeds,
            "cost_basis": sale.total_cost_basis,
            "capital_gain": sale.capital_gain,
            "is_long_term": sale.is_long_term,
            "gain_type": sale.gain_type,
        },
        "total_economic_gain": (sale.proceeds - Decimal("0")).quantize(Decimal("0.01")),
        "tax_treatment": {
            "ordinary_income": vesting.gross_income,
            "capital_gain": sale.capital_gain,
            "notes": [
                f"Ordinary income of ${vesting.gross_income:,.2f} at vesting (W-2)",
                f"{'Long-term' if sale.is_long_term else 'Short-term'} capital gain of ${sale.capital_gain:,.2f}",
                f"Withholding at vesting: ${withholding.total_withholding:,.2f} ({withholding.effective_withholding_rate * 100:.1f}%)",
            ],
        },
    }


# ============================================================
# Common RSU Scenarios
# ============================================================

def rsu_same_day_sale_example() -> dict:
    """
    Example: Same-day sale (sell immediately at vesting).
    
    Scenario:
    - 100 shares vest at $150/share
    - Sold immediately at $150/share
    
    Result: $15,000 ordinary income, $0 capital gain
    """
    shares = Decimal("100")
    fmv = Decimal("150")
    
    vesting_date = date(2025, 3, 15)
    sale_date = date(2025, 3, 15)  # Same day
    
    result = analyze_rsu_scenario(
        shares=shares,
        fmv_at_vesting=fmv,
        sale_price=fmv,
        vesting_date=vesting_date,
        sale_date=sale_date,
    )
    
    result["scenario"] = "Same-Day Sale"
    result["notes"] = [
        "Most common RSU scenario",
        "Zero capital gain risk",
        "Simplest tax situation",
        "All income is ordinary (W-2)",
    ]
    
    return result


def rsu_hold_and_sell_higher_example() -> dict:
    """
    Example: Hold RSU shares and sell at higher price.
    
    Scenario:
    - 100 shares vest at $150/share
    - Held for 18 months, sold at $200/share
    
    Result: $15,000 ordinary income + $5,000 LTCG
    """
    shares = Decimal("100")
    fmv = Decimal("150")
    sale_price = Decimal("200")
    
    vesting_date = date(2024, 1, 15)
    sale_date = date(2025, 7, 20)  # 18 months later
    
    result = analyze_rsu_scenario(
        shares=shares,
        fmv_at_vesting=fmv,
        sale_price=sale_price,
        vesting_date=vesting_date,
        sale_date=sale_date,
    )
    
    result["scenario"] = "Hold and Sell Higher (LTCG)"
    result["notes"] = [
        "Additional $5,000 gain taxed at LTCG rates (0-20%)",
        "Best case: stock went up and held >1 year",
        "Long-term capital gains rate is preferential",
    ]
    
    return result


def rsu_hold_and_sell_lower_example() -> dict:
    """
    Example: Hold RSU shares but stock drops.
    
    Scenario:
    - 100 shares vest at $150/share
    - Held for 8 months, sold at $100/share
    
    Result: $15,000 ordinary income (already taxed), $5,000 capital LOSS
    """
    shares = Decimal("100")
    fmv = Decimal("150")
    sale_price = Decimal("100")
    
    vesting_date = date(2024, 6, 15)
    sale_date = date(2025, 2, 20)  # 8 months later
    
    result = analyze_rsu_scenario(
        shares=shares,
        fmv_at_vesting=fmv,
        sale_price=sale_price,
        vesting_date=vesting_date,
        sale_date=sale_date,
    )
    
    result["scenario"] = "Hold and Stock Drops (Loss)"
    result["notes"] = [
        "⚠️ You still paid tax on $15,000 at vesting!",
        "Capital loss of $5,000 can offset other gains",
        "If no gains, can deduct up to $3,000/year against ordinary income",
        "This is why same-day sale is popular - eliminates stock price risk",
    ]
    
    return result
