"""
Tests for What-If Tax Scenario Engine.

Tests cover:
- Scenario parameter creation
- Tax calculation for scenarios
- Scenario comparison
- RSU timing scenarios
- ISO exercise scenarios
- Bonus timing scenarios
- State move scenarios
- Capital gains timing
- Optimization recommendations
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine.what_if import (
    ScenarioType,
    ScenarioParameters,
    WhatIfScenario,
    TaxResult,
    ScenarioComparison,
    WhatIfEngine,
    create_rsu_timing_scenarios,
    create_iso_exercise_scenarios,
    create_bonus_timing_scenarios,
    create_state_move_scenarios,
    create_capital_gains_timing_scenarios,
    calculate_marginal_tax_impact,
    find_optimal_iso_exercise,
    generate_optimization_recommendations,
)
from taxlens_engine.models import FilingStatus


# ============================================================
# Basic Data Model Tests
# ============================================================

class TestScenarioParameters:
    """Tests for ScenarioParameters."""
    
    def test_default_parameters(self):
        params = ScenarioParameters()
        
        assert params.name == "Baseline"
        assert params.scenario_type == ScenarioType.BASELINE
        assert params.filing_status == FilingStatus.SINGLE
        assert params.w2_wages == Decimal("0")
    
    def test_total_income_calculation(self):
        params = ScenarioParameters(
            w2_wages=Decimal("200000"),
            rsu_income=Decimal("50000"),
            bonus_income=Decimal("30000"),
            long_term_gains=Decimal("20000"),
            qualified_dividends=Decimal("5000"),
        )
        
        assert params.total_ordinary_income == Decimal("280000")
        assert params.total_preferential_income == Decimal("25000")
        assert params.total_income == Decimal("305000")
    
    def test_filing_status_variations(self):
        single = ScenarioParameters(filing_status=FilingStatus.SINGLE)
        married = ScenarioParameters(filing_status=FilingStatus.MARRIED_JOINTLY)
        
        assert single.filing_status == FilingStatus.SINGLE
        assert married.filing_status == FilingStatus.MARRIED_JOINTLY


class TestTaxResult:
    """Tests for TaxResult."""
    
    def test_total_tax_calculation(self):
        result = TaxResult(
            federal_tax=Decimal("40000"),
            state_tax=Decimal("15000"),
            fica_tax=Decimal("12000"),
            amt=Decimal("5000"),
            niit=Decimal("2000"),
        )
        
        assert result.total_tax == Decimal("74000")
    
    def test_empty_result(self):
        result = TaxResult()
        
        assert result.total_tax == Decimal("0")


class TestScenarioComparison:
    """Tests for ScenarioComparison."""
    
    def test_tax_savings_calculation(self):
        baseline = WhatIfScenario(
            parameters=ScenarioParameters(name="Baseline"),
            result=TaxResult(federal_tax=Decimal("50000")),
        )
        alternative = WhatIfScenario(
            parameters=ScenarioParameters(name="Alternative"),
            result=TaxResult(federal_tax=Decimal("40000")),
        )
        
        comparison = ScenarioComparison(baseline=baseline, alternative=alternative)
        
        assert comparison.tax_savings == Decimal("10000")
        assert comparison.tax_increase == Decimal("-10000")
    
    def test_breakdown_diff(self):
        baseline = WhatIfScenario(
            parameters=ScenarioParameters(),
            result=TaxResult(
                federal_tax=Decimal("40000"),
                state_tax=Decimal("15000"),
            ),
        )
        alternative = WhatIfScenario(
            parameters=ScenarioParameters(),
            result=TaxResult(
                federal_tax=Decimal("35000"),
                state_tax=Decimal("12000"),
            ),
        )
        
        comparison = ScenarioComparison(baseline=baseline, alternative=alternative)
        diff = comparison.get_breakdown_diff()
        
        assert diff["federal_tax"] == Decimal("-5000")
        assert diff["state_tax"] == Decimal("-3000")


# ============================================================
# WhatIfEngine Tests
# ============================================================

class TestWhatIfEngine:
    """Tests for WhatIfEngine."""
    
    def test_engine_initialization(self):
        engine = WhatIfEngine(tax_year=2025)
        
        assert engine.tax_year == 2025
        assert engine.scenarios == []
        assert engine.baseline is None
    
    def test_calculate_basic_scenario(self):
        engine = WhatIfEngine()
        params = ScenarioParameters(
            w2_wages=Decimal("150000"),
            filing_status=FilingStatus.SINGLE,
            state_code="CA",
        )
        
        scenario = engine.calculate_scenario(params)
        
        assert scenario.result.total_tax > Decimal("0")
        assert scenario.result.federal_tax > Decimal("0")
        assert scenario.result.state_tax > Decimal("0")
        assert scenario.result.fica_tax > Decimal("0")
        assert scenario.effective_rate > Decimal("0")
    
    def test_set_baseline(self):
        engine = WhatIfEngine()
        params = ScenarioParameters(
            w2_wages=Decimal("200000"),
            name="My Baseline",
        )
        
        baseline = engine.set_baseline(params)
        
        assert engine.baseline == baseline
        assert baseline in engine.scenarios
        assert baseline.parameters.scenario_type == ScenarioType.BASELINE
    
    def test_add_scenario_with_delta(self):
        engine = WhatIfEngine()
        
        # Set baseline
        baseline_params = ScenarioParameters(w2_wages=Decimal("200000"))
        engine.set_baseline(baseline_params)
        
        # Add higher income scenario
        alt_params = ScenarioParameters(
            name="Higher Income",
            w2_wages=Decimal("250000"),
        )
        alt_scenario = engine.add_scenario(alt_params)
        
        # Delta should be positive (more tax)
        assert alt_scenario.delta_from_baseline > Decimal("0")
    
    def test_compare_scenarios(self):
        engine = WhatIfEngine()
        
        params1 = ScenarioParameters(w2_wages=Decimal("150000"))
        params2 = ScenarioParameters(w2_wages=Decimal("200000"))
        
        scenario1 = engine.calculate_scenario(params1)
        scenario2 = engine.calculate_scenario(params2)
        
        comparison = engine.compare(scenario1, scenario2)
        
        # Higher income should have higher tax
        assert comparison.tax_increase > Decimal("0")
    
    def test_get_best_scenario(self):
        engine = WhatIfEngine()
        
        # Add multiple scenarios
        engine.set_baseline(ScenarioParameters(w2_wages=Decimal("200000")))
        engine.add_scenario(ScenarioParameters(w2_wages=Decimal("150000"), name="Lower"))
        engine.add_scenario(ScenarioParameters(w2_wages=Decimal("250000"), name="Higher"))
        
        best = engine.get_best_scenario()
        
        assert best is not None
        assert best.parameters.name == "Lower"
    
    def test_scenario_summary(self):
        engine = WhatIfEngine()
        
        engine.set_baseline(ScenarioParameters(w2_wages=Decimal("200000")))
        engine.add_scenario(ScenarioParameters(w2_wages=Decimal("150000"), name="Lower"))
        
        summary = engine.get_scenario_summary()
        
        assert summary["scenario_count"] == 2
        assert summary["baseline_tax"] > Decimal("0")
        assert summary["best_scenario"] == "Lower"


class TestScenarioCalculations:
    """Tests for specific tax calculations in scenarios."""
    
    def test_ltcg_tax_calculation(self):
        engine = WhatIfEngine()
        params = ScenarioParameters(
            w2_wages=Decimal("100000"),
            long_term_gains=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
        )
        
        scenario = engine.calculate_scenario(params)
        
        # LTCG should be taxed at preferential rate
        assert scenario.result.ltcg_tax >= Decimal("0")
    
    def test_amt_calculation_with_iso(self):
        engine = WhatIfEngine()
        params = ScenarioParameters(
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
        )
        
        scenario = engine.calculate_scenario(params)
        
        # ISO exercise should trigger AMT
        assert scenario.result.amt > Decimal("0")
    
    def test_niit_calculation(self):
        engine = WhatIfEngine()
        params = ScenarioParameters(
            w2_wages=Decimal("200000"),
            long_term_gains=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
        )
        
        scenario = engine.calculate_scenario(params)
        
        # Above NIIT threshold, should have NIIT
        assert scenario.result.niit > Decimal("0")
    
    def test_no_state_tax_for_wa(self):
        engine = WhatIfEngine()
        params = ScenarioParameters(
            w2_wages=Decimal("200000"),
            state_code="WA",
        )
        
        scenario = engine.calculate_scenario(params)
        
        assert scenario.result.state_tax == Decimal("0")
    
    def test_married_filing_jointly(self):
        engine = WhatIfEngine()
        
        single = ScenarioParameters(
            w2_wages=Decimal("200000"),
            filing_status=FilingStatus.SINGLE,
        )
        married = ScenarioParameters(
            w2_wages=Decimal("200000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
        )
        
        single_scenario = engine.calculate_scenario(single)
        married_scenario = engine.calculate_scenario(married)
        
        # MFJ should have lower tax due to wider brackets
        assert married_scenario.result.federal_tax < single_scenario.result.federal_tax


# ============================================================
# Scenario Builder Tests
# ============================================================

class TestRSUTimingScenarios:
    """Tests for RSU timing scenario creation."""
    
    def test_create_rsu_scenarios(self):
        baseline = ScenarioParameters(w2_wages=Decimal("200000"))
        
        scenarios = create_rsu_timing_scenarios(
            baseline,
            rsu_value=Decimal("100000"),
            current_year_vest_pct=Decimal("0.5"),
        )
        
        assert len(scenarios) == 2
        
        # Full vest scenario
        full_vest = scenarios[0]
        assert full_vest.rsu_income == Decimal("100000")
        
        # Partial vest scenario
        partial = scenarios[1]
        assert partial.rsu_income == Decimal("50000")
    
    def test_rsu_scenarios_have_correct_type(self):
        baseline = ScenarioParameters()
        scenarios = create_rsu_timing_scenarios(baseline, Decimal("50000"))
        
        for scenario in scenarios:
            assert scenario.scenario_type == ScenarioType.RSU_TIMING


class TestISOExerciseScenarios:
    """Tests for ISO exercise scenario creation."""
    
    def test_create_iso_scenarios(self):
        baseline = ScenarioParameters(w2_wages=Decimal("200000"))
        
        scenarios = create_iso_exercise_scenarios(
            baseline,
            iso_shares=1000,
            strike_price=Decimal("50"),
            current_fmv=Decimal("150"),
        )
        
        # Default increments: 0, 250, 500, 1000
        assert len(scenarios) == 4
        
        # Check bargain element calculation
        full_exercise = [s for s in scenarios if s.iso_shares_exercised == 1000][0]
        assert full_exercise.iso_bargain_element == Decimal("100000")  # (150-50) * 1000
    
    def test_iso_scenario_descriptions(self):
        baseline = ScenarioParameters()
        scenarios = create_iso_exercise_scenarios(
            baseline,
            iso_shares=500,
            strike_price=Decimal("25"),
            current_fmv=Decimal("100"),
        )
        
        # No exercise should mention no AMT
        no_exercise = [s for s in scenarios if s.iso_shares_exercised == 0][0]
        assert "no amt" in no_exercise.description.lower()


class TestBonusTimingScenarios:
    """Tests for bonus timing scenario creation."""
    
    def test_create_bonus_scenarios(self):
        baseline = ScenarioParameters(w2_wages=Decimal("200000"))
        
        scenarios = create_bonus_timing_scenarios(
            baseline,
            bonus_amount=Decimal("50000"),
            current_year_pct=Decimal("0.5"),
        )
        
        assert len(scenarios) == 3  # Full, defer, no bonus
        
        # Full bonus
        full = scenarios[0]
        assert full.bonus_income == Decimal("50000")
        
        # Deferred
        defer = scenarios[1]
        assert defer.bonus_income == Decimal("25000")
        
        # No bonus baseline
        no_bonus = scenarios[2]
        assert no_bonus.bonus_income == Decimal("0")


class TestStateMoveScenarios:
    """Tests for state move scenario creation."""
    
    def test_create_state_move_scenarios(self):
        baseline = ScenarioParameters(
            w2_wages=Decimal("200000"),
            state_code="CA",
        )
        
        scenarios = create_state_move_scenarios(
            baseline,
            new_state="WA",
            move_month=7,
        )
        
        assert len(scenarios) == 2
        
        # Stay in CA
        stay = scenarios[0]
        assert stay.state_code == "CA"
        
        # Move to WA
        move = scenarios[1]
        assert move.state_code == "WA"
    
    def test_state_move_has_correct_type(self):
        baseline = ScenarioParameters(state_code="NY")
        scenarios = create_state_move_scenarios(baseline, "FL")
        
        for scenario in scenarios:
            assert scenario.scenario_type == ScenarioType.STATE_MOVE


class TestCapitalGainsScenarios:
    """Tests for capital gains timing scenarios."""
    
    def test_create_ltcg_scenarios(self):
        baseline = ScenarioParameters(w2_wages=Decimal("200000"))
        
        scenarios = create_capital_gains_timing_scenarios(
            baseline,
            potential_gains=Decimal("100000"),
            is_long_term=True,
        )
        
        assert len(scenarios) == 3  # Realize, defer, partial
        
        # Full realization
        realize = scenarios[0]
        assert realize.long_term_gains == Decimal("100000")
        
        # Defer
        defer = scenarios[1]
        assert defer.long_term_gains == Decimal("0")
        
        # Partial
        partial = scenarios[2]
        assert partial.long_term_gains == Decimal("50000")
    
    def test_stcg_scenarios(self):
        baseline = ScenarioParameters()
        
        scenarios = create_capital_gains_timing_scenarios(
            baseline,
            potential_gains=Decimal("20000"),
            is_long_term=False,
        )
        
        realize = scenarios[0]
        assert realize.short_term_gains == Decimal("20000")


# ============================================================
# Analysis Function Tests
# ============================================================

class TestMarginalTaxImpact:
    """Tests for marginal tax impact calculation."""
    
    def test_ordinary_income_impact(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("200000"),
            filing_status=FilingStatus.SINGLE,
        )
        
        result = calculate_marginal_tax_impact(
            engine,
            baseline,
            additional_income=Decimal("10000"),
            income_type="ordinary",
        )
        
        assert result["additional_income"] == Decimal("10000")
        assert result["tax_increase"] > Decimal("0")
        assert result["marginal_rate"] > Decimal("0")
    
    def test_ltcg_impact(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
        )
        
        result = calculate_marginal_tax_impact(
            engine,
            baseline,
            additional_income=Decimal("10000"),
            income_type="ltcg",
        )
        
        # LTCG rate should be lower than ordinary
        assert result["marginal_rate"] <= Decimal("20")


class TestISOOptimization:
    """Tests for ISO exercise optimization."""
    
    def test_find_optimal_iso_exercise(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("200000"),
            filing_status=FilingStatus.SINGLE,
        )
        
        result = find_optimal_iso_exercise(
            engine,
            baseline,
            iso_shares=1000,
            strike_price=Decimal("50"),
            fmv=Decimal("150"),
            max_amt_exposure=Decimal("20000"),
        )
        
        assert result["optimal_shares"] >= 0
        assert result["optimal_shares"] <= 1000
        assert result["amt_exposure"] <= Decimal("20000")
    
    def test_iso_optimization_with_zero_amt_limit(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(w2_wages=Decimal("200000"))
        
        result = find_optimal_iso_exercise(
            engine,
            baseline,
            iso_shares=1000,
            strike_price=Decimal("50"),
            fmv=Decimal("150"),
            max_amt_exposure=Decimal("0"),
        )
        
        # With zero AMT limit, should exercise minimal shares
        # (some shares may still be possible if they don't trigger AMT)
        assert result["optimal_shares"] >= 0
        assert result["amt_exposure"] <= Decimal("0.01")  # Effectively zero


class TestOptimizationRecommendations:
    """Tests for optimization recommendations."""
    
    def test_generates_recommendations(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("300000"),
            long_term_gains=Decimal("100000"),
            state_code="CA",
        )
        
        recommendations = generate_optimization_recommendations(engine, baseline)
        
        assert len(recommendations) > 0
        
        # Should have various categories
        categories = [r["category"] for r in recommendations]
        assert len(categories) > 0
    
    def test_high_income_recommendation(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("500000"),  # High income
        )
        
        recommendations = generate_optimization_recommendations(engine, baseline)
        
        income_recs = [r for r in recommendations if r["category"] == "income_timing"]
        assert len(income_recs) > 0
    
    def test_iso_amt_recommendation(self):
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("100000"),  # Large ISO exposure
        )
        
        recommendations = generate_optimization_recommendations(engine, baseline)
        
        iso_recs = [r for r in recommendations if r["category"] == "iso_exercise"]
        assert len(iso_recs) > 0


# ============================================================
# Integration Tests
# ============================================================

class TestWhatIfIntegration:
    """Integration tests for what-if scenarios."""
    
    def test_tech_employee_comprehensive(self):
        """Test comprehensive scenario for typical tech employee."""
        engine = WhatIfEngine()
        
        # Baseline: CA tech employee with equity
        baseline = ScenarioParameters(
            name="Current Situation",
            w2_wages=Decimal("250000"),
            rsu_income=Decimal("100000"),
            long_term_gains=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            state_code="CA",
        )
        
        engine.set_baseline(baseline)
        
        # Alternative: Move to WA
        wa_scenario = engine.add_scenario(ScenarioParameters(
            name="Move to WA",
            w2_wages=Decimal("250000"),
            rsu_income=Decimal("100000"),
            long_term_gains=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            state_code="WA",
        ))
        
        # WA scenario should have lower total tax
        assert wa_scenario.delta_from_baseline < Decimal("0")
        
        # State tax should be zero
        assert wa_scenario.result.state_tax == Decimal("0")
    
    def test_iso_exercise_comparison(self):
        """Test comparing different ISO exercise amounts."""
        engine = WhatIfEngine()
        
        # No exercise
        baseline = ScenarioParameters(
            name="No Exercise",
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("0"),
        )
        engine.set_baseline(baseline)
        
        # Full exercise
        full = engine.add_scenario(ScenarioParameters(
            name="Full Exercise",
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("100000"),
        ))
        
        # Full exercise should have higher tax due to AMT
        assert full.delta_from_baseline > Decimal("0")
        assert full.result.amt > Decimal("0")
    
    def test_married_vs_single_comparison(self):
        """Test tax difference between filing statuses."""
        engine = WhatIfEngine()
        
        income = Decimal("400000")
        
        single = ScenarioParameters(
            name="Single",
            w2_wages=income,
            filing_status=FilingStatus.SINGLE,
        )
        engine.set_baseline(single)
        
        married = engine.add_scenario(ScenarioParameters(
            name="Married Filing Jointly",
            w2_wages=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
        ))
        
        # MFJ should have lower tax
        assert married.delta_from_baseline < Decimal("0")
    
    def test_scenario_persistence(self):
        """Test that scenarios are properly tracked."""
        engine = WhatIfEngine()
        
        engine.set_baseline(ScenarioParameters(name="Base", w2_wages=Decimal("100000")))
        engine.add_scenario(ScenarioParameters(name="Alt1", w2_wages=Decimal("120000")))
        engine.add_scenario(ScenarioParameters(name="Alt2", w2_wages=Decimal("150000")))
        
        assert len(engine.scenarios) == 3
        
        summary = engine.get_scenario_summary()
        assert summary["scenario_count"] == 3
