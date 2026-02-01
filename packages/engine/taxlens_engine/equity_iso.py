"""
ISO (Incentive Stock Options) calculations for TaxLens.

ISOs have special tax treatment:
- No ordinary income at exercise (unlike NSO)
- But creates AMT adjustment (bargain element)
- Qualifying disposition: All gain is long-term capital gain
- Disqualifying disposition: Bargain element becomes ordinary income

Key dates for ISO:
- Grant date: When options are granted
- Exercise date: When you buy the shares
- Sale date: When you sell the shares

Qualifying disposition requires:
- Hold shares > 1 year from exercise AND
- Hold shares > 2 years from grant
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from enum import Enum
from typing import Optional


class ISODispositionType(str, Enum):
    """Type of ISO disposition for tax purposes."""
    QUALIFYING = "qualifying"        # Favorable tax treatment
    DISQUALIFYING = "disqualifying"  # Ordinary income on bargain element


@dataclass
class ISOGrant:
    """
    Represents an ISO grant.
    
    ISOs are options to purchase company stock at a fixed price (strike).
    """
    grant_date: date
    shares_granted: Decimal
    strike_price: Decimal  # Exercise/purchase price
    expiration_date: Optional[date] = None  # Typically 10 years
    
    def shares_available_to_exercise(
        self,
        shares_already_exercised: Decimal = Decimal("0"),
    ) -> Decimal:
        """Calculate shares available to exercise."""
        return self.shares_granted - shares_already_exercised


@dataclass
class ISOExercise:
    """
    Represents exercising ISO options.
    
    At exercise:
    - You pay strike_price × shares for the shares
    - NO ordinary income (unlike NSO)
    - BUT bargain element is an AMT preference item
    """
    exercise_date: date
    shares_exercised: Decimal
    strike_price: Decimal  # Price you pay
    fmv_at_exercise: Decimal  # Fair Market Value at exercise
    grant_date: date  # Original grant date (for disposition type)
    
    @property
    def total_cost(self) -> Decimal:
        """Total cash paid to exercise."""
        return (self.shares_exercised * self.strike_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def bargain_element(self) -> Decimal:
        """
        Bargain element = (FMV - Strike) × shares.
        
        This is the AMT preference item. It's the "discount" you get.
        """
        spread = self.fmv_at_exercise - self.strike_price
        if spread <= 0:
            return Decimal("0")
        return (spread * self.shares_exercised).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def regular_tax_income(self) -> Decimal:
        """Regular tax income at exercise = $0 for ISO."""
        return Decimal("0")
    
    @property
    def amt_adjustment(self) -> Decimal:
        """AMT adjustment = bargain element."""
        return self.bargain_element
    
    @property
    def cost_basis_regular(self) -> Decimal:
        """Cost basis for regular tax = strike price."""
        return self.strike_price
    
    @property
    def cost_basis_amt(self) -> Decimal:
        """Cost basis for AMT = FMV at exercise."""
        return self.fmv_at_exercise


@dataclass
class ISOSale:
    """
    Represents selling ISO shares.
    
    The disposition type determines tax treatment.
    """
    sale_date: date
    shares_sold: Decimal
    sale_price: Decimal
    strike_price: Decimal  # Original exercise price
    fmv_at_exercise: Decimal  # FMV when exercised
    exercise_date: date
    grant_date: date
    
    @property
    def proceeds(self) -> Decimal:
        """Total sale proceeds."""
        return (self.shares_sold * self.sale_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def disposition_type(self) -> ISODispositionType:
        """
        Determine if this is a qualifying or disqualifying disposition.
        
        Qualifying requires BOTH:
        - > 1 year from exercise date
        - > 2 years from grant date
        """
        days_from_exercise = (self.sale_date - self.exercise_date).days
        days_from_grant = (self.sale_date - self.grant_date).days
        
        if days_from_exercise > 365 and days_from_grant > 730:
            return ISODispositionType.QUALIFYING
        return ISODispositionType.DISQUALIFYING
    
    @property
    def is_qualifying(self) -> bool:
        """Convenience check for qualifying disposition."""
        return self.disposition_type == ISODispositionType.QUALIFYING
    
    @property
    def bargain_element(self) -> Decimal:
        """Original bargain element (FMV at exercise - strike)."""
        spread = self.fmv_at_exercise - self.strike_price
        if spread <= 0:
            return Decimal("0")
        return (spread * self.shares_sold).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def ordinary_income(self) -> Decimal:
        """
        Ordinary income from sale (W-2 income).
        
        - Qualifying: $0
        - Disqualifying: Lesser of (1) bargain element or (2) actual gain
        """
        if self.is_qualifying:
            return Decimal("0")
        
        # Disqualifying disposition
        actual_gain = self.proceeds - (self.shares_sold * self.strike_price)
        
        # If stock went down, ordinary income is limited to actual gain
        # (or zero if there's a loss)
        if actual_gain <= 0:
            return Decimal("0")
        
        return min(self.bargain_element, actual_gain).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def capital_gain(self) -> Decimal:
        """
        Capital gain portion.
        
        - Qualifying: All gain (sale price - strike) is LTCG
        - Disqualifying: Gain above bargain element
        """
        if self.is_qualifying:
            # All gain is long-term capital gain
            gain = self.proceeds - (self.shares_sold * self.strike_price)
            return gain.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Disqualifying: gain above ordinary income portion
        total_gain = self.proceeds - (self.shares_sold * self.strike_price)
        capital_portion = total_gain - self.ordinary_income
        return capital_portion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property
    def is_long_term_capital_gain(self) -> bool:
        """
        Is the capital gain portion long-term?
        
        - Qualifying: Always yes (by definition)
        - Disqualifying: Based on holding period from exercise
        """
        if self.is_qualifying:
            return True
        
        # Disqualifying: check actual holding period
        days_held = (self.sale_date - self.exercise_date).days
        return days_held >= 365


@dataclass
class ISOTaxSummary:
    """Summary of ISO tax implications."""
    disposition_type: ISODispositionType
    
    # Exercise
    shares: Decimal
    strike_price: Decimal
    fmv_at_exercise: Decimal
    bargain_element: Decimal
    
    # Sale
    sale_price: Decimal
    proceeds: Decimal
    
    # Tax treatment
    ordinary_income: Decimal
    capital_gain: Decimal
    is_long_term: bool
    
    # AMT
    amt_adjustment_at_exercise: Decimal
    potential_amt_credit: Decimal = Decimal("0")
    
    @property
    def total_gain(self) -> Decimal:
        """Total economic gain."""
        return (self.proceeds - self.shares * self.strike_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


def calculate_iso_exercise(
    shares: Decimal,
    strike_price: Decimal,
    fmv_at_exercise: Decimal,
    grant_date: date,
    exercise_date: date,
) -> ISOExercise:
    """
    Calculate tax implications of ISO exercise.
    
    Args:
        shares: Number of shares to exercise
        strike_price: Option strike price (what you pay)
        fmv_at_exercise: Fair Market Value at exercise
        grant_date: Original grant date
        exercise_date: Exercise date
        
    Returns:
        ISOExercise with calculated values
    """
    return ISOExercise(
        exercise_date=exercise_date,
        shares_exercised=shares,
        strike_price=strike_price,
        fmv_at_exercise=fmv_at_exercise,
        grant_date=grant_date,
    )


def calculate_iso_sale(
    shares: Decimal,
    sale_price: Decimal,
    strike_price: Decimal,
    fmv_at_exercise: Decimal,
    grant_date: date,
    exercise_date: date,
    sale_date: date,
) -> ISOSale:
    """
    Calculate tax implications of selling ISO shares.
    
    Args:
        shares: Number of shares to sell
        sale_price: Sale price per share
        strike_price: Original strike price
        fmv_at_exercise: FMV when exercised
        grant_date: Original grant date
        exercise_date: When options were exercised
        sale_date: Date of sale
        
    Returns:
        ISOSale with calculated values
    """
    return ISOSale(
        sale_date=sale_date,
        shares_sold=shares,
        sale_price=sale_price,
        strike_price=strike_price,
        fmv_at_exercise=fmv_at_exercise,
        exercise_date=exercise_date,
        grant_date=grant_date,
    )


def estimate_amt_impact(
    bargain_element: Decimal,
    regular_taxable_income: Decimal,
    filing_status: str = "single",
) -> dict:
    """
    Estimate AMT impact from ISO exercise.
    
    This is a simplified estimate. Full AMT calculation requires
    the complete tax calculator.
    
    Args:
        bargain_element: ISO bargain element (AMT adjustment)
        regular_taxable_income: Regular taxable income
        filing_status: "single" or "married_jointly"
        
    Returns:
        Dict with estimated AMT impact
    """
    # 2025 AMT exemptions
    if filing_status == "married_jointly":
        exemption = Decimal("137000")
        phaseout_start = Decimal("1252700")
    else:
        exemption = Decimal("88100")
        phaseout_start = Decimal("626350")
    
    # AMT income
    amt_income = regular_taxable_income + bargain_element
    
    # Phaseout
    if amt_income > phaseout_start:
        reduction = (amt_income - phaseout_start) * Decimal("0.25")
        exemption = max(Decimal("0"), exemption - reduction)
    
    amt_taxable = max(Decimal("0"), amt_income - exemption)
    
    # AMT rates: 26% up to $232,600, 28% above
    amt_threshold = Decimal("232600")
    if amt_taxable <= amt_threshold:
        tentative_amt = amt_taxable * Decimal("0.26")
    else:
        tentative_amt = (
            amt_threshold * Decimal("0.26") +
            (amt_taxable - amt_threshold) * Decimal("0.28")
        )
    
    # Rough estimate of regular tax (simplified)
    regular_tax_estimate = regular_taxable_income * Decimal("0.30")
    
    amt_owed = max(Decimal("0"), tentative_amt - regular_tax_estimate)
    
    return {
        "bargain_element": bargain_element,
        "amt_income": amt_income.quantize(Decimal("0.01")),
        "amt_exemption": exemption.quantize(Decimal("0.01")),
        "amt_taxable": amt_taxable.quantize(Decimal("0.01")),
        "tentative_minimum_tax": tentative_amt.quantize(Decimal("0.01")),
        "estimated_amt_owed": amt_owed.quantize(Decimal("0.01")),
        "warning": "This is an estimate. Use full calculator for accurate AMT.",
    }


def analyze_iso_scenario(
    shares: Decimal,
    strike_price: Decimal,
    fmv_at_exercise: Decimal,
    sale_price: Decimal,
    grant_date: date,
    exercise_date: date,
    sale_date: date,
) -> ISOTaxSummary:
    """
    Complete analysis of an ISO exercise and sale.
    
    Args:
        shares: Number of shares
        strike_price: Option strike price
        fmv_at_exercise: FMV when exercised
        sale_price: Sale price
        grant_date: Original grant date
        exercise_date: Exercise date
        sale_date: Sale date
        
    Returns:
        Complete ISOTaxSummary
    """
    sale = calculate_iso_sale(
        shares=shares,
        sale_price=sale_price,
        strike_price=strike_price,
        fmv_at_exercise=fmv_at_exercise,
        grant_date=grant_date,
        exercise_date=exercise_date,
        sale_date=sale_date,
    )
    
    return ISOTaxSummary(
        disposition_type=sale.disposition_type,
        shares=shares,
        strike_price=strike_price,
        fmv_at_exercise=fmv_at_exercise,
        bargain_element=sale.bargain_element,
        sale_price=sale_price,
        proceeds=sale.proceeds,
        ordinary_income=sale.ordinary_income,
        capital_gain=sale.capital_gain,
        is_long_term=sale.is_long_term_capital_gain,
        amt_adjustment_at_exercise=sale.bargain_element,
    )


# ============================================================
# Common ISO Scenarios
# ============================================================

def iso_qualifying_disposition_example() -> dict:
    """
    Example: ISO with qualifying disposition.
    
    Scenario:
    - Granted 1,000 shares at $10 strike
    - Exercised when FMV = $50
    - Sold at $100 after holding requirements met
    
    Result: All $90,000 gain is LTCG (no ordinary income)
    """
    shares = Decimal("1000")
    strike = Decimal("10")
    fmv_exercise = Decimal("50")
    sale_price = Decimal("100")
    
    grant_date = date(2022, 1, 1)
    exercise_date = date(2023, 6, 1)  # > 1 year from grant
    sale_date = date(2025, 1, 15)  # > 2 years from grant, > 1 year from exercise
    
    summary = analyze_iso_scenario(
        shares=shares,
        strike_price=strike,
        fmv_at_exercise=fmv_exercise,
        sale_price=sale_price,
        grant_date=grant_date,
        exercise_date=exercise_date,
        sale_date=sale_date,
    )
    
    return {
        "scenario": "ISO Qualifying Disposition",
        "shares": shares,
        "strike_price": strike,
        "fmv_at_exercise": fmv_exercise,
        "sale_price": sale_price,
        "grant_date": str(grant_date),
        "exercise_date": str(exercise_date),
        "sale_date": str(sale_date),
        "disposition_type": summary.disposition_type.value,
        "bargain_element": summary.bargain_element,
        "ordinary_income": summary.ordinary_income,
        "capital_gain": summary.capital_gain,
        "is_long_term": summary.is_long_term,
        "total_gain": summary.total_gain,
        "notes": [
            "No ordinary income at exercise",
            f"AMT adjustment at exercise: ${summary.bargain_element:,.2f}",
            "All gain is long-term capital gain",
            "Maximum 20% federal rate on gain (vs 37% ordinary)",
        ],
    }


def iso_disqualifying_disposition_example() -> dict:
    """
    Example: ISO with disqualifying disposition.
    
    Scenario:
    - Granted 1,000 shares at $10 strike
    - Exercised when FMV = $50
    - Sold at $80 before holding requirements met
    
    Result: $40,000 ordinary income + $30,000 STCG
    """
    shares = Decimal("1000")
    strike = Decimal("10")
    fmv_exercise = Decimal("50")
    sale_price = Decimal("80")
    
    grant_date = date(2024, 1, 1)
    exercise_date = date(2024, 7, 1)
    sale_date = date(2025, 3, 1)  # < 1 year from exercise
    
    summary = analyze_iso_scenario(
        shares=shares,
        strike_price=strike,
        fmv_at_exercise=fmv_exercise,
        sale_price=sale_price,
        grant_date=grant_date,
        exercise_date=exercise_date,
        sale_date=sale_date,
    )
    
    return {
        "scenario": "ISO Disqualifying Disposition",
        "shares": shares,
        "strike_price": strike,
        "fmv_at_exercise": fmv_exercise,
        "sale_price": sale_price,
        "grant_date": str(grant_date),
        "exercise_date": str(exercise_date),
        "sale_date": str(sale_date),
        "disposition_type": summary.disposition_type.value,
        "bargain_element": summary.bargain_element,
        "ordinary_income": summary.ordinary_income,
        "capital_gain": summary.capital_gain,
        "is_long_term": summary.is_long_term,
        "total_gain": summary.total_gain,
        "notes": [
            f"Ordinary income (W-2): ${summary.ordinary_income:,.2f}",
            f"Capital gain: ${summary.capital_gain:,.2f}",
            "Ordinary income = lesser of bargain element or actual gain",
            "This eliminates AMT paid at exercise (AMT credit)",
        ],
    }


def iso_underwater_sale_example() -> dict:
    """
    Example: ISO sold below exercise FMV (stock dropped).
    
    Scenario:
    - Exercised at FMV = $50
    - Stock dropped, sold at $30
    
    Result: Limited ordinary income, capital loss
    """
    shares = Decimal("1000")
    strike = Decimal("10")
    fmv_exercise = Decimal("50")
    sale_price = Decimal("30")
    
    grant_date = date(2024, 1, 1)
    exercise_date = date(2024, 7, 1)
    sale_date = date(2025, 3, 1)
    
    summary = analyze_iso_scenario(
        shares=shares,
        strike_price=strike,
        fmv_at_exercise=fmv_exercise,
        sale_price=sale_price,
        grant_date=grant_date,
        exercise_date=exercise_date,
        sale_date=sale_date,
    )
    
    return {
        "scenario": "ISO Underwater Sale (Stock Dropped)",
        "shares": shares,
        "strike_price": strike,
        "fmv_at_exercise": fmv_exercise,
        "sale_price": sale_price,
        "disposition_type": summary.disposition_type.value,
        "bargain_element": summary.bargain_element,
        "ordinary_income": summary.ordinary_income,
        "capital_gain": summary.capital_gain,
        "total_gain": summary.total_gain,
        "notes": [
            "Bargain element was $40,000 but stock dropped",
            f"Ordinary income limited to actual gain: ${summary.ordinary_income:,.2f}",
            "May have AMT from exercise that becomes a credit",
            "Painful scenario: paid AMT on paper gain that evaporated",
        ],
    }
