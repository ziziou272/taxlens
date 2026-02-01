"""
What-If Tax Scenario Engine for TaxLens.

Enables interactive tax planning through scenario modeling:
- RSU vesting date changes
- ISO exercise timing optimization
- Bonus timing strategies
- State residency changes
- Capital gains timing

Compares scenarios to calculate tax deltas and identify optimization opportunities.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from enum import Enum
from typing import Optional, Callable
from copy import deepcopy

from .models import FilingStatus, TaxYear, IncomeBreakdown
from .federal import (
    calculate_federal_tax,
    calculate_ltcg_tax,
    calculate_amt,
    calculate_fica,
    calculate_niit,
)
from .california import calculate_california_tax


class ScenarioType(str, Enum):
    """Types of what-if scenarios."""
    BASELINE = "baseline"
    RSU_TIMING = "rsu_timing"
    ISO_EXERCISE = "iso_exercise"
    BONUS_TIMING = "bonus_timing"
    STATE_MOVE = "state_move"
    CAPITAL_GAINS = "capital_gains"
    INCOME_SHIFT = "income_shift"
    CUSTOM = "custom"


@dataclass
class TaxResult:
    """Complete tax calculation result."""
    federal_tax: Decimal = Decimal("0")
    state_tax: Decimal = Decimal("0")
    fica_tax: Decimal = Decimal("0")
    amt: Decimal = Decimal("0")
    niit: Decimal = Decimal("0")
    ltcg_tax: Decimal = Decimal("0")
    
    @property
    def total_tax(self) -> Decimal:
        """Total tax liability."""
        return (
            self.federal_tax +
            self.state_tax +
            self.fica_tax +
            self.amt +
            self.niit
        )
    
    @property
    def effective_rate(self) -> Decimal:
        """Effective tax rate (set externally based on income)."""
        return Decimal("0")


@dataclass
class ScenarioParameters:
    """
    Parameters for a what-if scenario.
    
    Modify these to create different scenarios.
    """
    # Basic info
    name: str = "Baseline"
    description: str = ""
    scenario_type: ScenarioType = ScenarioType.BASELINE
    
    # Income parameters
    w2_wages: Decimal = Decimal("0")
    rsu_income: Decimal = Decimal("0")
    nso_income: Decimal = Decimal("0")
    bonus_income: Decimal = Decimal("0")
    
    # Capital gains
    short_term_gains: Decimal = Decimal("0")
    long_term_gains: Decimal = Decimal("0")
    qualified_dividends: Decimal = Decimal("0")
    interest_income: Decimal = Decimal("0")
    
    # ISO/AMT related
    iso_bargain_element: Decimal = Decimal("0")
    iso_shares_exercised: int = 0
    iso_strike_price: Decimal = Decimal("0")
    iso_fmv_at_exercise: Decimal = Decimal("0")
    
    # Filing info
    filing_status: FilingStatus = FilingStatus.SINGLE
    tax_year: int = 2025
    
    # State info
    state_code: str = "CA"
    state_days_resident: int = 365
    
    # Withholding (for comparison)
    federal_withheld: Decimal = Decimal("0")
    state_withheld: Decimal = Decimal("0")
    
    # Deductions
    use_standard_deduction: bool = True
    itemized_deductions: Decimal = Decimal("0")
    
    @property
    def total_ordinary_income(self) -> Decimal:
        """Total ordinary income."""
        return (
            self.w2_wages +
            self.rsu_income +
            self.nso_income +
            self.bonus_income +
            self.short_term_gains +
            self.interest_income
        )
    
    @property
    def total_preferential_income(self) -> Decimal:
        """Total preferential income (LTCG + QDIV)."""
        return self.long_term_gains + self.qualified_dividends
    
    @property
    def total_income(self) -> Decimal:
        """Total gross income."""
        return self.total_ordinary_income + self.total_preferential_income


@dataclass
class WhatIfScenario:
    """
    A what-if tax scenario with calculated results.
    """
    parameters: ScenarioParameters
    result: TaxResult = field(default_factory=TaxResult)
    
    # Calculated metrics
    taxable_income: Decimal = Decimal("0")
    effective_rate: Decimal = Decimal("0")
    marginal_rate: Decimal = Decimal("0")
    balance_due: Decimal = Decimal("0")  # Positive = owe, negative = refund
    
    # Comparison to baseline
    delta_from_baseline: Decimal = Decimal("0")
    delta_percentage: Decimal = Decimal("0")
    
    # Breakdown
    breakdown: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass
class ScenarioComparison:
    """Comparison between two scenarios."""
    baseline: WhatIfScenario
    alternative: WhatIfScenario
    
    @property
    def tax_savings(self) -> Decimal:
        """Tax savings (positive = alternative saves money)."""
        return self.baseline.result.total_tax - self.alternative.result.total_tax
    
    @property
    def tax_increase(self) -> Decimal:
        """Tax increase (positive = alternative costs more)."""
        return -self.tax_savings
    
    @property
    def savings_percentage(self) -> Decimal:
        """Percentage savings."""
        if self.baseline.result.total_tax > 0:
            return (self.tax_savings / self.baseline.result.total_tax) * 100
        return Decimal("0")
    
    def get_breakdown_diff(self) -> dict:
        """Get line-by-line difference."""
        return {
            "federal_tax": self.alternative.result.federal_tax - self.baseline.result.federal_tax,
            "state_tax": self.alternative.result.state_tax - self.baseline.result.state_tax,
            "fica_tax": self.alternative.result.fica_tax - self.baseline.result.fica_tax,
            "amt": self.alternative.result.amt - self.baseline.result.amt,
            "niit": self.alternative.result.niit - self.baseline.result.niit,
            "total": self.alternative.result.total_tax - self.baseline.result.total_tax,
        }


class WhatIfEngine:
    """
    Engine for running what-if tax scenarios.
    """
    
    def __init__(self, tax_year: int = 2025):
        self.tax_year = tax_year
        self.tax_year_config = TaxYear(year=tax_year)
        self.scenarios: list[WhatIfScenario] = []
        self.baseline: Optional[WhatIfScenario] = None
    
    def calculate_scenario(self, params: ScenarioParameters) -> WhatIfScenario:
        """
        Calculate taxes for a scenario.
        
        Args:
            params: Scenario parameters
            
        Returns:
            WhatIfScenario with calculated results
        """
        scenario = WhatIfScenario(parameters=params)
        
        # Get standard deduction
        std_deduction = self.tax_year_config.get_standard_deduction(params.filing_status)
        deduction = std_deduction if params.use_standard_deduction else params.itemized_deductions
        
        # Calculate taxable income
        taxable_ordinary = max(Decimal("0"), params.total_ordinary_income - deduction)
        scenario.taxable_income = taxable_ordinary + params.total_preferential_income
        
        # Calculate federal tax on ordinary income
        federal_ordinary = calculate_federal_tax(
            taxable_income=taxable_ordinary,
            filing_status=params.filing_status,
        )
        
        # Calculate LTCG tax
        ltcg_tax = Decimal("0")
        if params.total_preferential_income > 0:
            ltcg_tax = calculate_ltcg_tax(
                long_term_gains=params.total_preferential_income,
                taxable_ordinary_income=taxable_ordinary,
                filing_status=params.filing_status,
            )
        
        scenario.result.federal_tax = federal_ordinary
        scenario.result.ltcg_tax = ltcg_tax
        
        # Calculate AMT if applicable
        if params.iso_bargain_element > 0:
            amt_income, tentative_minimum_tax, _ = calculate_amt(
                regular_taxable_income=taxable_ordinary,
                iso_bargain_element=params.iso_bargain_element,
                filing_status=params.filing_status,
            )
            # AMT owed is the amount TMT exceeds regular tax
            # The function returns 0 for amt_owed, we need to calculate it
            scenario.result.amt = max(Decimal("0"), tentative_minimum_tax - federal_ordinary)
        
        # Calculate FICA
        fica_wages = params.w2_wages + params.rsu_income + params.nso_income
        fica_result = calculate_fica(
            w2_wages=fica_wages,
            filing_status=params.filing_status,
        )
        # fica_result is a tuple: (social_security, medicare, additional_medicare)
        scenario.result.fica_tax = fica_result[0] + fica_result[1] + fica_result[2]
        
        # Calculate NIIT
        investment_income = (
            params.long_term_gains +
            params.short_term_gains +
            params.qualified_dividends +
            params.interest_income
        )
        niit = calculate_niit(
            investment_income=investment_income,
            magi=params.total_income,
            filing_status=params.filing_status,
        )
        scenario.result.niit = niit
        
        # Calculate state tax
        if params.state_code == "CA":
            scenario.result.state_tax = calculate_california_tax(
                taxable_income=scenario.taxable_income,
                filing_status=params.filing_status,
            )
        else:
            # Simplified state tax for other states
            scenario.result.state_tax = self._estimate_state_tax(
                params.state_code,
                scenario.taxable_income,
            )
        
        # Calculate effective rate
        if params.total_income > 0:
            scenario.effective_rate = (
                scenario.result.total_tax / params.total_income * 100
            ).quantize(Decimal("0.01"))
        
        # Calculate balance due
        total_withheld = params.federal_withheld + params.state_withheld
        scenario.balance_due = scenario.result.total_tax - total_withheld
        
        # Create breakdown
        scenario.breakdown = {
            "gross_income": params.total_income,
            "deduction": deduction,
            "taxable_income": scenario.taxable_income,
            "federal_tax": scenario.result.federal_tax,
            "ltcg_tax": scenario.result.ltcg_tax,
            "state_tax": scenario.result.state_tax,
            "fica_tax": scenario.result.fica_tax,
            "amt": scenario.result.amt,
            "niit": scenario.result.niit,
            "total_tax": scenario.result.total_tax,
            "effective_rate": scenario.effective_rate,
        }
        
        return scenario
    
    def _estimate_state_tax(self, state_code: str, taxable_income: Decimal) -> Decimal:
        """
        Estimate state tax for non-CA states.
        
        This is a simplified estimate. Real implementation would need
        full state tax brackets.
        """
        # No income tax states
        no_tax_states = {"WA", "TX", "FL", "NV", "WY", "SD", "AK", "TN", "NH"}
        if state_code in no_tax_states:
            return Decimal("0")
        
        # Simplified flat rates (approximate highest marginal rates)
        state_rates = {
            "NY": Decimal("0.0685"),
            "NJ": Decimal("0.0675"),
            "MA": Decimal("0.05"),
            "IL": Decimal("0.0495"),
            "PA": Decimal("0.0307"),
            "OH": Decimal("0.04"),
            "GA": Decimal("0.055"),
            "NC": Decimal("0.0525"),
            "VA": Decimal("0.0575"),
            "CO": Decimal("0.044"),
            "AZ": Decimal("0.025"),
            "OR": Decimal("0.099"),
            "MN": Decimal("0.0985"),
            "WI": Decimal("0.0765"),
            "MD": Decimal("0.0575"),
            "CT": Decimal("0.0699"),
        }
        
        rate = state_rates.get(state_code, Decimal("0.05"))
        return (taxable_income * rate).quantize(Decimal("0.01"))
    
    def set_baseline(self, params: ScenarioParameters) -> WhatIfScenario:
        """
        Set the baseline scenario for comparison.
        
        Args:
            params: Baseline parameters
            
        Returns:
            Baseline scenario
        """
        params.name = params.name or "Baseline"
        params.scenario_type = ScenarioType.BASELINE
        self.baseline = self.calculate_scenario(params)
        self.scenarios = [self.baseline]
        return self.baseline
    
    def add_scenario(self, params: ScenarioParameters) -> WhatIfScenario:
        """
        Add an alternative scenario for comparison.
        
        Args:
            params: Alternative scenario parameters
            
        Returns:
            Alternative scenario with delta from baseline
        """
        scenario = self.calculate_scenario(params)
        
        if self.baseline:
            scenario.delta_from_baseline = (
                scenario.result.total_tax - self.baseline.result.total_tax
            )
            if self.baseline.result.total_tax > 0:
                scenario.delta_percentage = (
                    scenario.delta_from_baseline / self.baseline.result.total_tax * 100
                ).quantize(Decimal("0.01"))
        
        self.scenarios.append(scenario)
        return scenario
    
    def compare(self, scenario1: WhatIfScenario, scenario2: WhatIfScenario) -> ScenarioComparison:
        """
        Compare two scenarios.
        
        Args:
            scenario1: First scenario (baseline)
            scenario2: Second scenario (alternative)
            
        Returns:
            ScenarioComparison with tax delta
        """
        return ScenarioComparison(baseline=scenario1, alternative=scenario2)
    
    def get_best_scenario(self) -> Optional[WhatIfScenario]:
        """Get the scenario with lowest total tax."""
        if not self.scenarios:
            return None
        return min(self.scenarios, key=lambda s: s.result.total_tax)
    
    def get_scenario_summary(self) -> dict:
        """Get summary of all scenarios."""
        if not self.scenarios:
            return {}
        
        best = self.get_best_scenario()
        worst = max(self.scenarios, key=lambda s: s.result.total_tax)
        
        return {
            "scenario_count": len(self.scenarios),
            "baseline_tax": self.baseline.result.total_tax if self.baseline else None,
            "best_scenario": best.parameters.name if best else None,
            "best_tax": best.result.total_tax if best else None,
            "worst_scenario": worst.parameters.name,
            "worst_tax": worst.result.total_tax,
            "max_savings": (worst.result.total_tax - best.result.total_tax) if best else Decimal("0"),
        }


# ============================================================
# Scenario Builder Helpers
# ============================================================

def create_rsu_timing_scenarios(
    baseline_params: ScenarioParameters,
    rsu_value: Decimal,
    current_year_vest_pct: Decimal = Decimal("1.0"),
) -> list[ScenarioParameters]:
    """
    Create scenarios for RSU vesting timing.
    
    Compares vesting all in current year vs deferring some to next year.
    
    Args:
        baseline_params: Baseline scenario parameters
        rsu_value: Total RSU value to vest
        current_year_vest_pct: Percentage to vest in current year (0-1)
        
    Returns:
        List of scenario parameters
    """
    scenarios = []
    
    # Scenario: Vest all this year
    vest_all = deepcopy(baseline_params)
    vest_all.name = "Vest All RSU This Year"
    vest_all.description = f"Vest all ${rsu_value:,.2f} of RSU in current tax year"
    vest_all.scenario_type = ScenarioType.RSU_TIMING
    vest_all.rsu_income = rsu_value
    scenarios.append(vest_all)
    
    # Scenario: Split vesting
    if current_year_vest_pct < Decimal("1.0"):
        split_vest = deepcopy(baseline_params)
        split_vest.name = f"Defer {(1 - current_year_vest_pct) * 100:.0f}% RSU to Next Year"
        split_vest.rsu_income = rsu_value * current_year_vest_pct
        split_vest.scenario_type = ScenarioType.RSU_TIMING
        split_vest.description = (
            f"Vest ${rsu_value * current_year_vest_pct:,.2f} this year, "
            f"defer ${rsu_value * (1 - current_year_vest_pct):,.2f} to next year"
        )
        scenarios.append(split_vest)
    
    return scenarios


def create_iso_exercise_scenarios(
    baseline_params: ScenarioParameters,
    iso_shares: int,
    strike_price: Decimal,
    current_fmv: Decimal,
    share_increments: list[int] = None,
) -> list[ScenarioParameters]:
    """
    Create scenarios for ISO exercise timing.
    
    Compares exercising different amounts of ISO shares.
    
    Args:
        baseline_params: Baseline scenario parameters
        iso_shares: Total ISO shares available
        strike_price: Strike price per share
        current_fmv: Current fair market value per share
        share_increments: List of share amounts to model
        
    Returns:
        List of scenario parameters
    """
    if share_increments is None:
        share_increments = [0, iso_shares // 4, iso_shares // 2, iso_shares]
    
    scenarios = []
    bargain_per_share = current_fmv - strike_price
    
    for shares in share_increments:
        if shares > iso_shares:
            continue
        
        scenario = deepcopy(baseline_params)
        scenario.name = f"Exercise {shares:,} ISO Shares"
        scenario.scenario_type = ScenarioType.ISO_EXERCISE
        scenario.iso_shares_exercised = shares
        scenario.iso_strike_price = strike_price
        scenario.iso_fmv_at_exercise = current_fmv
        scenario.iso_bargain_element = bargain_per_share * Decimal(str(shares))
        
        if shares == 0:
            scenario.description = "No ISO exercise - no AMT exposure"
        else:
            scenario.description = (
                f"Exercise {shares:,} shares: "
                f"${bargain_per_share * shares:,.2f} bargain element (AMT preference)"
            )
        
        scenarios.append(scenario)
    
    return scenarios


def create_bonus_timing_scenarios(
    baseline_params: ScenarioParameters,
    bonus_amount: Decimal,
    current_year_pct: Decimal = Decimal("1.0"),
) -> list[ScenarioParameters]:
    """
    Create scenarios for bonus timing.
    
    Compares taking bonus this year vs deferring to next year.
    
    Args:
        baseline_params: Baseline scenario parameters
        bonus_amount: Total bonus amount
        current_year_pct: Percentage to take in current year
        
    Returns:
        List of scenario parameters
    """
    scenarios = []
    
    # Full bonus this year
    full_bonus = deepcopy(baseline_params)
    full_bonus.name = "Full Bonus This Year"
    full_bonus.scenario_type = ScenarioType.BONUS_TIMING
    full_bonus.bonus_income = bonus_amount
    full_bonus.description = f"Receive full ${bonus_amount:,.2f} bonus in current year"
    scenarios.append(full_bonus)
    
    # Defer bonus to next year
    if current_year_pct < Decimal("1.0"):
        defer_bonus = deepcopy(baseline_params)
        defer_bonus.name = "Defer Bonus to Next Year"
        defer_bonus.scenario_type = ScenarioType.BONUS_TIMING
        defer_bonus.bonus_income = bonus_amount * current_year_pct
        defer_bonus.description = (
            f"Take ${bonus_amount * current_year_pct:,.2f} this year, "
            f"defer ${bonus_amount * (1 - current_year_pct):,.2f} to next year"
        )
        scenarios.append(defer_bonus)
    
    # No bonus (for comparison)
    no_bonus = deepcopy(baseline_params)
    no_bonus.name = "No Bonus (Baseline)"
    no_bonus.scenario_type = ScenarioType.BONUS_TIMING
    no_bonus.bonus_income = Decimal("0")
    no_bonus.description = "Baseline without bonus for reference"
    scenarios.append(no_bonus)
    
    return scenarios


def create_state_move_scenarios(
    baseline_params: ScenarioParameters,
    new_state: str,
    move_month: int = 7,
) -> list[ScenarioParameters]:
    """
    Create scenarios for state residency change.
    
    Compares staying vs moving to a new state mid-year.
    
    Args:
        baseline_params: Baseline scenario parameters
        new_state: State to move to
        move_month: Month of move (1-12)
        
    Returns:
        List of scenario parameters
    """
    scenarios = []
    
    # Stay in current state
    stay = deepcopy(baseline_params)
    stay.name = f"Stay in {baseline_params.state_code}"
    stay.scenario_type = ScenarioType.STATE_MOVE
    stay.description = f"Full year resident of {baseline_params.state_code}"
    scenarios.append(stay)
    
    # Move to new state
    move = deepcopy(baseline_params)
    move.name = f"Move to {new_state} in Month {move_month}"
    move.scenario_type = ScenarioType.STATE_MOVE
    move.state_code = new_state
    days_in_old_state = int(365 * (move_month - 1) / 12)
    move.state_days_resident = 365 - days_in_old_state
    move.description = (
        f"Move from {baseline_params.state_code} to {new_state} mid-year. "
        f"Part-year resident of both states."
    )
    # Note: Real implementation would need to prorate income between states
    scenarios.append(move)
    
    return scenarios


def create_capital_gains_timing_scenarios(
    baseline_params: ScenarioParameters,
    potential_gains: Decimal,
    is_long_term: bool = True,
) -> list[ScenarioParameters]:
    """
    Create scenarios for capital gains timing.
    
    Compares realizing gains this year vs deferring.
    
    Args:
        baseline_params: Baseline scenario parameters
        potential_gains: Potential capital gains
        is_long_term: Whether gains are long-term
        
    Returns:
        List of scenario parameters
    """
    scenarios = []
    
    # Realize gains this year
    realize = deepcopy(baseline_params)
    realize.name = "Realize Gains This Year"
    realize.scenario_type = ScenarioType.CAPITAL_GAINS
    if is_long_term:
        realize.long_term_gains = baseline_params.long_term_gains + potential_gains
        realize.description = f"Realize ${potential_gains:,.2f} in long-term capital gains"
    else:
        realize.short_term_gains = baseline_params.short_term_gains + potential_gains
        realize.description = f"Realize ${potential_gains:,.2f} in short-term capital gains"
    scenarios.append(realize)
    
    # Defer gains
    defer = deepcopy(baseline_params)
    defer.name = "Defer Gains to Next Year"
    defer.scenario_type = ScenarioType.CAPITAL_GAINS
    defer.description = f"Hold positions, defer ${potential_gains:,.2f} gains to next year"
    scenarios.append(defer)
    
    # Partial realization
    partial = deepcopy(baseline_params)
    partial.name = "Realize Half This Year"
    partial.scenario_type = ScenarioType.CAPITAL_GAINS
    half_gains = potential_gains / 2
    if is_long_term:
        partial.long_term_gains = baseline_params.long_term_gains + half_gains
    else:
        partial.short_term_gains = baseline_params.short_term_gains + half_gains
    partial.description = f"Realize ${half_gains:,.2f}, defer ${half_gains:,.2f}"
    scenarios.append(partial)
    
    return scenarios


# ============================================================
# Analysis Functions
# ============================================================

def calculate_marginal_tax_impact(
    engine: WhatIfEngine,
    baseline: ScenarioParameters,
    additional_income: Decimal,
    income_type: str = "ordinary",
) -> dict:
    """
    Calculate the marginal tax impact of additional income.
    
    Args:
        engine: WhatIfEngine instance
        baseline: Baseline parameters
        additional_income: Additional income to model
        income_type: Type of income (ordinary, ltcg, qdiv)
        
    Returns:
        Dict with marginal rate and tax impact
    """
    baseline_scenario = engine.calculate_scenario(baseline)
    
    with_income = deepcopy(baseline)
    if income_type == "ordinary":
        with_income.w2_wages += additional_income
    elif income_type == "ltcg":
        with_income.long_term_gains += additional_income
    elif income_type == "qdiv":
        with_income.qualified_dividends += additional_income
    elif income_type == "interest":
        with_income.interest_income += additional_income
    
    with_income_scenario = engine.calculate_scenario(with_income)
    
    tax_increase = with_income_scenario.result.total_tax - baseline_scenario.result.total_tax
    marginal_rate = (tax_increase / additional_income * 100).quantize(Decimal("0.01"))
    
    return {
        "additional_income": additional_income,
        "income_type": income_type,
        "tax_increase": tax_increase,
        "marginal_rate": marginal_rate,
        "baseline_tax": baseline_scenario.result.total_tax,
        "new_tax": with_income_scenario.result.total_tax,
    }


def find_optimal_iso_exercise(
    engine: WhatIfEngine,
    baseline: ScenarioParameters,
    iso_shares: int,
    strike_price: Decimal,
    fmv: Decimal,
    max_amt_exposure: Decimal = Decimal("50000"),
) -> dict:
    """
    Find optimal ISO exercise amount to limit AMT exposure.
    
    Args:
        engine: WhatIfEngine instance
        baseline: Baseline parameters
        iso_shares: Total ISO shares available
        strike_price: Strike price per share
        fmv: Fair market value per share
        max_amt_exposure: Maximum acceptable AMT
        
    Returns:
        Dict with optimal exercise amount and analysis
    """
    bargain_per_share = fmv - strike_price
    
    # Binary search for optimal shares
    low, high = 0, iso_shares
    optimal_shares = 0
    
    while low <= high:
        mid = (low + high) // 2
        
        test_params = deepcopy(baseline)
        test_params.iso_shares_exercised = mid
        test_params.iso_bargain_element = bargain_per_share * Decimal(str(mid))
        
        scenario = engine.calculate_scenario(test_params)
        
        if scenario.result.amt <= max_amt_exposure:
            optimal_shares = mid
            low = mid + 1
        else:
            high = mid - 1
    
    # Calculate final scenario
    final_params = deepcopy(baseline)
    final_params.iso_shares_exercised = optimal_shares
    final_params.iso_bargain_element = bargain_per_share * Decimal(str(optimal_shares))
    final_scenario = engine.calculate_scenario(final_params)
    
    return {
        "optimal_shares": optimal_shares,
        "bargain_element": final_params.iso_bargain_element,
        "amt_exposure": final_scenario.result.amt,
        "total_tax": final_scenario.result.total_tax,
        "remaining_shares": iso_shares - optimal_shares,
        "max_amt_limit": max_amt_exposure,
    }


def generate_optimization_recommendations(
    engine: WhatIfEngine,
    baseline: ScenarioParameters,
) -> list[dict]:
    """
    Generate tax optimization recommendations based on profile.
    
    Args:
        engine: WhatIfEngine instance
        baseline: Baseline parameters
        
    Returns:
        List of optimization recommendations
    """
    recommendations = []
    baseline_scenario = engine.set_baseline(baseline)
    
    # Check if high income puts them in high bracket
    if baseline.total_ordinary_income > Decimal("200000"):
        recommendations.append({
            "category": "income_timing",
            "title": "Consider Income Deferral",
            "description": "High income may benefit from deferring income to future years.",
            "potential_savings": "Varies",
            "priority": "medium",
        })
    
    # Check for large LTCG
    if baseline.long_term_gains > Decimal("50000"):
        # Model partial deferral
        defer_params = deepcopy(baseline)
        defer_params.long_term_gains = baseline.long_term_gains / 2
        defer_scenario = engine.calculate_scenario(defer_params)
        savings = baseline_scenario.result.total_tax - defer_scenario.result.total_tax
        
        if savings > Decimal("1000"):
            recommendations.append({
                "category": "capital_gains",
                "title": "Consider Deferring Capital Gains",
                "description": f"Deferring half of LTCG could save ${savings:,.2f}",
                "potential_savings": savings,
                "priority": "high" if savings > Decimal("5000") else "medium",
            })
    
    # Check for ISO exercise opportunity
    if baseline.iso_bargain_element > 0:
        # Check if AMT is triggered
        if baseline_scenario.result.amt > Decimal("0"):
            recommendations.append({
                "category": "iso_exercise",
                "title": "Review ISO Exercise Amount",
                "description": "Current ISO exercise triggers AMT. Consider spreading exercises.",
                "potential_savings": baseline_scenario.result.amt,
                "priority": "high",
            })
    
    # Check for state tax optimization
    if baseline.state_code == "CA" and baseline.total_income > Decimal("300000"):
        # Model WA scenario (no income tax)
        wa_params = deepcopy(baseline)
        wa_params.state_code = "WA"
        wa_scenario = engine.calculate_scenario(wa_params)
        savings = baseline_scenario.result.state_tax
        
        recommendations.append({
            "category": "state_residency",
            "title": "Consider Tax-Free State",
            "description": f"Moving to WA could save ${savings:,.2f} in state tax",
            "potential_savings": savings,
            "priority": "low",  # Major life change
        })
    
    return recommendations
