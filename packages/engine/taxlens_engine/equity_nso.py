"""
NSO (Non-Qualified Stock Options) calculations for TaxLens.

NSOs are simpler than ISOs:
- At exercise: Ordinary income = (FMV - Strike) × shares
- This is W-2 income with tax withholding
- Cost basis = FMV at exercise
- Future gain/loss is capital gain

No special holding period requirements.
No AMT implications (already taxed as ordinary income).
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Optional


@dataclass
class NSOGrant:
    """
    Represents an NSO grant.
    """
    grant_date: date
    shares_granted: Decimal
    strike_price: Decimal
    vesting_schedule: Optional[str] = None  # e.g., "4 year, 1 year cliff"
    expiration_date: Optional[date] = None


@dataclass
class NSOExercise:
    """
    Represents exercising NSO options.
    
    Unlike ISOs, NSOs create ordinary income at exercise.
    """
    exercise_date: date
    shares_exercised: Decimal
    strike_price: Decimal
    fmv_at_exercise: Decimal
    
    @property
    def total_cost(self) -> Decimal:
        """Cash paid to exercise."""
        return (self.shares_exercised * self.strike_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def spread(self) -> Decimal:
        """Spread per share (FMV - Strike)."""
        return max(Decimal("0"), self.fmv_at_exercise - self.strike_price)
    
    @property
    def ordinary_income(self) -> Decimal:
        """
        Ordinary income at exercise.
        
        This is W-2 income and will have taxes withheld.
        """
        income = self.spread * self.shares_exercised
        return income.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property
    def cost_basis_per_share(self) -> Decimal:
        """Cost basis = FMV at exercise (includes spread that was taxed)."""
        return self.fmv_at_exercise


@dataclass
class NSOSale:
    """
    Represents selling NSO shares after exercise.
    """
    sale_date: date
    shares_sold: Decimal
    sale_price: Decimal
    cost_basis_per_share: Decimal  # FMV at exercise
    exercise_date: date
    
    @property
    def proceeds(self) -> Decimal:
        """Sale proceeds."""
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
        """Capital gain (or loss)."""
        return self.proceeds - self.total_cost_basis
    
    @property
    def holding_days(self) -> int:
        """Days held since exercise."""
        return (self.sale_date - self.exercise_date).days
    
    @property
    def is_long_term(self) -> bool:
        """Is this long-term capital gain (> 1 year)."""
        return self.holding_days >= 365


@dataclass
class NSOTaxSummary:
    """Summary of NSO tax implications."""
    # Exercise
    shares: Decimal
    strike_price: Decimal
    fmv_at_exercise: Decimal
    ordinary_income: Decimal  # W-2 income
    
    # Sale (if applicable)
    sale_price: Optional[Decimal] = None
    capital_gain: Optional[Decimal] = None
    is_long_term: Optional[bool] = None
    
    # Withholding estimate
    estimated_withholding: Optional[Decimal] = None
    
    @property
    def total_gain(self) -> Decimal:
        """Total economic gain."""
        exercise_gain = self.ordinary_income
        sale_gain = self.capital_gain or Decimal("0")
        return exercise_gain + sale_gain


def calculate_nso_exercise(
    shares: Decimal,
    strike_price: Decimal,
    fmv_at_exercise: Decimal,
    exercise_date: date,
) -> NSOExercise:
    """
    Calculate NSO exercise.
    
    Args:
        shares: Shares to exercise
        strike_price: Option strike price
        fmv_at_exercise: FMV at exercise
        exercise_date: Date of exercise
        
    Returns:
        NSOExercise with calculated values
    """
    return NSOExercise(
        exercise_date=exercise_date,
        shares_exercised=shares,
        strike_price=strike_price,
        fmv_at_exercise=fmv_at_exercise,
    )


def estimate_nso_withholding(
    ordinary_income: Decimal,
    federal_supplemental_rate: Decimal = Decimal("0.22"),
    state_rate: Decimal = Decimal("0.1023"),  # CA
    social_security_rate: Decimal = Decimal("0.062"),
    medicare_rate: Decimal = Decimal("0.0145"),
    over_ss_limit: bool = False,
) -> dict:
    """
    Estimate withholding on NSO exercise income.
    
    NSO income is supplemental wages with flat rate withholding.
    
    Args:
        ordinary_income: Ordinary income from exercise
        federal_supplemental_rate: Federal supplemental rate (22% under $1M)
        state_rate: State rate (CA: 10.23%)
        social_security_rate: SS rate (0 if over limit)
        medicare_rate: Medicare rate
        over_ss_limit: Whether already over SS wage base
        
    Returns:
        Dict with withholding breakdown
    """
    federal = (ordinary_income * federal_supplemental_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    state = (ordinary_income * state_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    ss = Decimal("0")
    if not over_ss_limit:
        ss = (ordinary_income * social_security_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    medicare = (ordinary_income * medicare_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    total = federal + state + ss + medicare
    
    return {
        "federal": federal,
        "state": state,
        "social_security": ss,
        "medicare": medicare,
        "total": total,
        "effective_rate": (total / ordinary_income).quantize(
            Decimal("0.0001")
        ) if ordinary_income > 0 else Decimal("0"),
    }


def nso_exercise_and_hold_example() -> dict:
    """
    Example: NSO exercise and hold.
    
    Scenario:
    - 1,000 options at $10 strike
    - Exercise when FMV = $50
    - Hold for future sale
    """
    shares = Decimal("1000")
    strike = Decimal("10")
    fmv = Decimal("50")
    
    exercise = calculate_nso_exercise(
        shares=shares,
        strike_price=strike,
        fmv_at_exercise=fmv,
        exercise_date=date(2025, 6, 1),
    )
    
    withholding = estimate_nso_withholding(exercise.ordinary_income)
    
    return {
        "scenario": "NSO Exercise and Hold",
        "shares": shares,
        "strike_price": strike,
        "fmv_at_exercise": fmv,
        "cash_to_exercise": exercise.total_cost,
        "ordinary_income": exercise.ordinary_income,
        "withholding": withholding,
        "cost_basis": exercise.cost_basis_per_share,
        "notes": [
            f"Pay ${exercise.total_cost:,.2f} to exercise",
            f"W-2 income: ${exercise.ordinary_income:,.2f}",
            f"Estimated withholding: ${withholding['total']:,.2f}",
            f"Cost basis for future sale: ${exercise.cost_basis_per_share}/share",
            "Any future gain above FMV is capital gain",
        ],
    }


def nso_cashless_exercise_example() -> dict:
    """
    Example: Cashless NSO exercise (sell to cover).
    
    Scenario:
    - 1,000 options at $10 strike
    - Exercise and sell when FMV = $50
    - No capital gain (sold immediately)
    """
    shares = Decimal("1000")
    strike = Decimal("10")
    fmv = Decimal("50")
    
    exercise = calculate_nso_exercise(
        shares=shares,
        strike_price=strike,
        fmv_at_exercise=fmv,
        exercise_date=date(2025, 6, 1),
    )
    
    # Sell immediately
    sale = NSOSale(
        sale_date=date(2025, 6, 1),
        shares_sold=shares,
        sale_price=fmv,
        cost_basis_per_share=fmv,
        exercise_date=date(2025, 6, 1),
    )
    
    withholding = estimate_nso_withholding(exercise.ordinary_income)
    
    return {
        "scenario": "NSO Cashless Exercise",
        "shares": shares,
        "strike_price": strike,
        "sale_price": fmv,
        "ordinary_income": exercise.ordinary_income,
        "capital_gain": sale.capital_gain,  # Should be $0
        "gross_proceeds": sale.proceeds,
        "estimated_net_proceeds": sale.proceeds - withholding["total"],
        "notes": [
            "No cash needed (sell to cover)",
            f"All ${exercise.ordinary_income:,.2f} is ordinary income",
            "No capital gain (sold at same price)",
            f"Net cash received: ~${sale.proceeds - withholding['total']:,.2f}",
        ],
    }
