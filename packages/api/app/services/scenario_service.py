"""Scenario service — delegates to taxlens_engine what_if."""
from decimal import Decimal

from taxlens_engine.models import FilingStatus
from taxlens_engine.what_if import (
    WhatIfEngine,
    ScenarioParameters,
    ScenarioType,
)

from app.schemas.scenario import (
    ScenarioInput,
    ScenarioRunInput,
    ScenarioResultResponse,
    ScenarioComparisonResponse,
    ScenarioTypeResponse,
)


SCENARIO_TYPES = [
    ScenarioTypeResponse(type_id="rsu_timing", name="RSU Vesting Timing", description="Compare vesting all RSU this year vs deferring"),
    ScenarioTypeResponse(type_id="iso_exercise", name="ISO Exercise", description="Model ISO exercise amounts and AMT impact"),
    ScenarioTypeResponse(type_id="bonus_timing", name="Bonus Timing", description="Compare taking bonus this year vs deferring"),
    ScenarioTypeResponse(type_id="state_move", name="State Residency Change", description="Compare staying vs moving to a new state"),
    ScenarioTypeResponse(type_id="capital_gains", name="Capital Gains Timing", description="Model realizing gains now vs deferring"),
    ScenarioTypeResponse(type_id="income_shift", name="Income Shifting", description="Shift income between years"),
    ScenarioTypeResponse(type_id="custom", name="Custom Scenario", description="Build a custom what-if scenario"),
]


def _to_params(inp: ScenarioInput) -> ScenarioParameters:
    return ScenarioParameters(
        name=inp.name,
        scenario_type=ScenarioType(inp.scenario_type) if inp.scenario_type in [e.value for e in ScenarioType] else ScenarioType.CUSTOM,
        w2_wages=Decimal(str(inp.wages)),
        rsu_income=Decimal(str(inp.rsu_income)),
        nso_income=Decimal(str(inp.nso_income)),
        bonus_income=Decimal(str(inp.bonus_income)),
        short_term_gains=Decimal(str(inp.short_term_gains)),
        long_term_gains=Decimal(str(inp.long_term_gains)),
        qualified_dividends=Decimal(str(inp.qualified_dividends)),
        interest_income=Decimal(str(inp.interest_income)),
        iso_bargain_element=Decimal(str(inp.iso_bargain_element)),
        filing_status=FilingStatus(inp.filing_status),
        state_code=inp.state,
        itemized_deductions=Decimal(str(inp.itemized_deductions)),
        use_standard_deduction=inp.itemized_deductions == 0,
    )


def _to_result(scenario) -> ScenarioResultResponse:
    return ScenarioResultResponse(
        name=scenario.parameters.name,
        total_tax=float(scenario.result.total_tax),
        effective_rate=float(scenario.effective_rate),
        breakdown={k: float(v) if isinstance(v, Decimal) else v for k, v in scenario.breakdown.items()},
    )


def get_types() -> list[ScenarioTypeResponse]:
    return SCENARIO_TYPES


def run_comparison(inp: ScenarioRunInput) -> ScenarioComparisonResponse:
    engine = WhatIfEngine()
    baseline = engine.set_baseline(_to_params(inp.baseline))
    alt = engine.add_scenario(_to_params(inp.alternative))
    comparison = engine.compare(baseline, alt)

    return ScenarioComparisonResponse(
        baseline=_to_result(baseline),
        alternative=_to_result(alt),
        tax_savings=float(comparison.tax_savings),
        savings_percentage=float(comparison.savings_percentage),
        breakdown_diff={k: float(v) for k, v in comparison.get_breakdown_diff().items()},
    )
