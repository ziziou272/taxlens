"""
Integration tests for TaxLens Engine.

These tests validate end-to-end workflows combining multiple modules:
- Complete tax calculation pipelines
- Data import to tax calculation flows
- Red flag analysis with real scenarios
- What-if scenario comparisons
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine import (
    calculate_taxes,
    FilingStatus,
    IncomeBreakdown,
)
from taxlens_engine.federal import (
    calculate_federal_tax,
    calculate_ltcg_tax,
    calculate_amt,
    calculate_fica,
    calculate_niit,
)
from taxlens_engine.california import calculate_california_tax
from taxlens_engine.equity_rsu import (
    RSUGrant,
    RSUVesting,
    calculate_rsu_vesting,
    calculate_rsu_sale,
    analyze_rsu_scenario,
)
from taxlens_engine.equity_iso import (
    ISOGrant,
    ISOExercise,
    calculate_iso_exercise,
    calculate_iso_sale,
    analyze_iso_scenario,
)
from taxlens_engine.red_flags import analyze_red_flags
from taxlens_engine.red_flags_enhanced import (
    analyze_red_flags_enhanced,
    StatePresence,
    StockTransaction,
)
from taxlens_engine.what_if import (
    WhatIfEngine,
    ScenarioParameters,
    create_rsu_timing_scenarios,
    create_iso_exercise_scenarios,
    create_state_move_scenarios,
)
from taxlens_engine.importers import (
    parse_fidelity_csv,
    parse_schwab_csv,
    W2Entry,
    TaxProfile,
    StockSaleEntry,
    VestingEventEntry,
)


class TestTechEmployeeFullYear:
    """
    Integration test: Full year for a typical tech employee.
    
    Scenario:
    - Base salary: $250,000
    - RSU vesting: $150,000 (quarterly)
    - LTCG from previous RSU sales: $50,000
    - Filing: Single, CA resident
    """
    
    def test_full_year_calculation(self):
        """Test complete tax calculation for tech employee."""
        income = IncomeBreakdown(
            w2_wages=Decimal("250000"),
            rsu_income=Decimal("150000"),
            long_term_gains=Decimal("50000"),
        )
        
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Verify all components are calculated
        assert result.federal_tax_total > Decimal("0")
        assert result.state_tax > Decimal("0")
        assert result.social_security_tax > Decimal("0")
        assert result.medicare_tax > Decimal("0")
        
        # Verify total tax is reasonable (30-50% effective rate)
        total_income = income.total_income
        assert result.total_tax > total_income * Decimal("0.30")
        assert result.total_tax < total_income * Decimal("0.50")
        
        # Verify effective rate is calculated
        assert result.effective_rate > Decimal("0")
        assert result.effective_rate < Decimal("50")
    
    def test_tax_breakdown_accuracy(self):
        """Test that individual tax components sum correctly."""
        income = IncomeBreakdown(
            w2_wages=Decimal("200000"),
            rsu_income=Decimal("100000"),
        )
        
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Verify federal components
        federal_components = (
            result.federal_tax_on_ordinary +
            result.federal_tax_on_ltcg +
            result.amt_owed
        )
        assert abs(result.federal_tax_total - federal_components) < Decimal("1")
        
        # Verify FICA components
        fica_total = (
            result.social_security_tax +
            result.medicare_tax +
            result.additional_medicare_tax
        )
        assert fica_total > Decimal("0")


class TestISOExerciseIntegration:
    """
    Integration test: ISO exercise with AMT impact.
    
    Scenario:
    - Base income: $200,000
    - ISO exercise: 1,000 shares at $50 strike, $150 FMV
    - Bargain element: $100,000
    """
    
    def test_iso_exercise_triggers_amt(self):
        """Test that ISO exercise properly triggers AMT."""
        base_income = Decimal("200000")
        iso_bargain = Decimal("100000")
        
        # Calculate regular tax
        std_deduction = Decimal("15000")
        taxable = base_income - std_deduction
        regular_tax = calculate_federal_tax(taxable, FilingStatus.SINGLE)
        
        # Calculate AMT
        amt_income, tmt, _ = calculate_amt(
            regular_taxable_income=taxable,
            iso_bargain_element=iso_bargain,
            filing_status=FilingStatus.SINGLE,
        )
        
        # TMT should exceed regular tax
        assert tmt > regular_tax
        
        # AMT owed is the difference
        amt_owed = tmt - regular_tax
        assert amt_owed > Decimal("0")
    
    def test_iso_calculation_integration(self):
        """Test ISO calculation with full scenario."""
        # Calculate exercise
        result = calculate_iso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("150"),
            grant_date=date(2020, 1, 15),
            exercise_date=date(2024, 6, 15),
        )
        
        assert result.shares_exercised == Decimal("1000")
        assert result.bargain_element == Decimal("100000")
        assert result.total_cost == Decimal("50000")
    
    def test_what_if_iso_comparison(self):
        """Test what-if comparison for ISO exercise amounts."""
        engine = WhatIfEngine()
        
        baseline = ScenarioParameters(
            name="No Exercise",
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("0"),
            state_code="CA",
        )
        engine.set_baseline(baseline)
        
        # Full exercise scenario
        full_exercise = ScenarioParameters(
            name="Exercise 1000 shares",
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("100000"),
            state_code="CA",
        )
        full_scenario = engine.add_scenario(full_exercise)
        
        # Full exercise should cost more due to AMT
        assert full_scenario.result.amt > Decimal("0")
        assert full_scenario.delta_from_baseline > Decimal("0")


class TestRSUVestingIntegration:
    """
    Integration test: RSU vesting and sale.
    
    Scenario:
    - RSU vesting: 400 shares at $200 FMV
    - Later sale: 200 shares at $250
    """
    
    def test_rsu_vesting_to_sale(self):
        """Test RSU from vesting through sale."""
        # Calculate vesting
        vest_result = calculate_rsu_vesting(
            shares=Decimal("400"),
            fmv=Decimal("200"),
            vesting_date=date(2025, 1, 15),
            state="CA",
            grant_date=date(2023, 1, 15),
        )
        
        assert vest_result["gross_income"] == Decimal("80000")
        assert vest_result["cost_basis_per_share"] == Decimal("200")
        
        # Calculate sale
        sale_result = calculate_rsu_sale(
            shares=Decimal("200"),
            sale_price=Decimal("250"),
            cost_basis_per_share=Decimal("200"),
            vesting_date=date(2025, 1, 15),
            sale_date=date(2025, 6, 15),
        )
        
        # Gain is $50/share * 200 shares = $10,000
        assert sale_result["capital_gain"] == Decimal("10000")
        assert sale_result["gain_type"] == "short_term"  # < 1 year
    
    def test_rsu_vesting_red_flags(self):
        """Test red flags for RSU vesting scenarios."""
        report = analyze_red_flags(
            total_income=Decimal("350000"),
            total_tax_liability=Decimal("100000"),
            total_withheld=Decimal("70000"),  # Underwithheld
            rsu_income=Decimal("100000"),
            filing_status="single",
            state="CA",
        )
        
        # Should detect underwithholding
        assert len(report.alerts) > 0
        underwithholding_alerts = [
            a for a in report.alerts 
            if "withholding" in a.title.lower()
        ]
        assert len(underwithholding_alerts) > 0


class TestDataImportToCalculation:
    """
    Integration test: Import data and calculate taxes.
    """
    
    def test_fidelity_import_to_vesting_summary(self):
        """Test importing Fidelity data and creating tax profile."""
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
03/15/2025,DEPOSIT STOCK,AAPL,RSU Q1 Vest,100,175.00,17500.00
06/15/2025,DEPOSIT STOCK,AAPL,RSU Q2 Vest,100,180.00,18000.00
09/15/2025,DEPOSIT STOCK,AAPL,RSU Q3 Vest,100,185.00,18500.00
12/15/2025,DEPOSIT STOCK,AAPL,RSU Q4 Vest,100,190.00,19000.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert result.success
        assert len(result.vesting_events) == 4
        
        # Calculate total RSU income
        total_rsu_income = sum(
            v["value"] for v in result.vesting_events
            if v["value"] is not None
        )
        assert total_rsu_income == Decimal("73000.00")
    
    def test_tax_profile_to_calculation(self):
        """Test building TaxProfile and calculating taxes."""
        profile = TaxProfile(
            tax_year=2025,
            filing_status="single",
            state_of_residence="CA",
        )
        
        # Add W-2
        profile.w2_entries.append(W2Entry(
            employer_name="Tech Corp",
            wages=Decimal("250000"),
            federal_withheld=Decimal("50000"),
            state_withheld=Decimal("20000"),
        ))
        
        # Add vesting events
        profile.vesting_events.append(VestingEventEntry(
            vest_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vest=Decimal("180"),
            federal_withheld=Decimal("3960"),
            state_withheld=Decimal("1836"),
        ))
        
        # Add stock sale
        profile.stock_sales.append(StockSaleEntry(
            sale_date=date(2025, 9, 15),
            symbol="TECH",
            shares_sold=Decimal("50"),
            sale_price=Decimal("200"),
            acquisition_date=date(2025, 3, 15),
            cost_basis_per_share=Decimal("180"),
        ))
        
        # Verify aggregations
        assert profile.total_w2_wages == Decimal("250000")
        assert profile.total_rsu_income == Decimal("18000")
        assert profile.total_short_term_gains == Decimal("1000")  # (200-180)*50


class TestMultiStateIntegration:
    """
    Integration test: Multi-state scenario.
    
    Scenario: CA resident who worked 60 days in NY
    """
    
    def test_state_nexus_detection(self):
        """Test state nexus warning generation."""
        report = analyze_red_flags_enhanced(
            current_date=date(2025, 6, 15),
            total_income=Decimal("400000"),
            total_tax_liability=Decimal("120000"),
            total_withheld=Decimal("100000"),
            ytd_income=Decimal("200000"),
            ytd_withheld=Decimal("50000"),
            estimated_payments_made={1: Decimal("15000"), 2: Decimal("15000")},
            primary_state="CA",
            other_state_presence=[
                StatePresence(
                    state_code="NY",
                    days_present=60,
                    days_worked=50,
                    income_earned=Decimal("80000"),
                )
            ],
            filing_status="single",
        )
        
        # Should detect NY work day tax issue
        ny_alerts = [a for a in report.alerts if "NY" in str(a.message)]
        assert len(ny_alerts) > 0


class TestWashSaleIntegration:
    """
    Integration test: Wash sale detection in trading activity.
    """
    
    def test_wash_sale_detection_flow(self):
        """Test full wash sale detection flow."""
        transactions = [
            # Buy shares
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("180"),
            ),
            # Sell at loss
            StockTransaction(
                date=date(2025, 3, 15),
                symbol="AAPL",
                action="sell",
                shares=Decimal("100"),
                price=Decimal("150"),
            ),
            # Buy back within 30 days
            StockTransaction(
                date=date(2025, 3, 25),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("155"),
            ),
        ]
        
        report = analyze_red_flags_enhanced(
            current_date=date(2025, 4, 1),
            total_income=Decimal("200000"),
            total_tax_liability=Decimal("50000"),
            total_withheld=Decimal("45000"),
            ytd_income=Decimal("100000"),
            ytd_withheld=Decimal("25000"),
            estimated_payments_made={1: Decimal("10000")},
            primary_state="CA",
            stock_transactions=transactions,
            filing_status="single",
        )
        
        # Should detect wash sale
        wash_alerts = [a for a in report.alerts if "wash" in a.title.lower()]
        assert len(wash_alerts) > 0


class TestWhatIfCompleteWorkflow:
    """
    Integration test: Complete what-if analysis workflow.
    """
    
    def test_comprehensive_what_if_analysis(self):
        """Test full what-if workflow for tax planning."""
        engine = WhatIfEngine()
        
        # Create baseline
        baseline = ScenarioParameters(
            name="Current Plan",
            w2_wages=Decimal("300000"),
            rsu_income=Decimal("150000"),
            long_term_gains=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            state_code="CA",
        )
        engine.set_baseline(baseline)
        
        # Test RSU timing scenarios
        rsu_scenarios = create_rsu_timing_scenarios(
            baseline,
            rsu_value=Decimal("100000"),
            current_year_vest_pct=Decimal("0.5"),
        )
        for params in rsu_scenarios:
            engine.add_scenario(params)
        
        # Test state move scenario
        state_scenarios = create_state_move_scenarios(baseline, "WA", move_month=7)
        for params in state_scenarios:
            engine.add_scenario(params)
        
        # Get best scenario
        best = engine.get_best_scenario()
        assert best is not None
        
        # WA scenario should have lowest tax (no state income tax)
        wa_scenarios = [
            s for s in engine.scenarios
            if s.parameters.state_code == "WA"
        ]
        if wa_scenarios:
            wa_scenario = wa_scenarios[0]
            assert wa_scenario.result.state_tax == Decimal("0")
    
    def test_iso_optimization_workflow(self):
        """Test ISO exercise optimization workflow."""
        engine = WhatIfEngine()
        
        baseline = ScenarioParameters(
            w2_wages=Decimal("200000"),
            state_code="CA",
        )
        
        # Create ISO scenarios
        iso_scenarios = create_iso_exercise_scenarios(
            baseline,
            iso_shares=2000,
            strike_price=Decimal("50"),
            current_fmv=Decimal("150"),
        )
        
        engine.set_baseline(iso_scenarios[0])  # No exercise
        for params in iso_scenarios[1:]:
            engine.add_scenario(params)
        
        # More shares = more AMT
        scenarios_by_shares = sorted(
            engine.scenarios,
            key=lambda s: s.parameters.iso_bargain_element
        )
        
        # Verify AMT increases with more shares
        prev_amt = Decimal("0")
        for scenario in scenarios_by_shares:
            if scenario.parameters.iso_bargain_element > Decimal("0"):
                assert scenario.result.amt >= prev_amt
                prev_amt = scenario.result.amt


class TestEdgeCasesIntegration:
    """
    Integration tests for edge cases.
    """
    
    def test_zero_income(self):
        """Test handling of zero income."""
        income = IncomeBreakdown()  # All zeros
        
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        assert result.total_tax == Decimal("0")
        assert result.effective_rate == Decimal("0")
    
    def test_very_high_income(self):
        """Test handling of very high income."""
        income = IncomeBreakdown(
            w2_wages=Decimal("2000000"),
            long_term_gains=Decimal("1000000"),
        )
        
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Should hit highest brackets
        assert result.total_tax > Decimal("1000000")
        # Effective rate is stored as decimal (0.4517 = 45.17%)
        assert result.effective_rate > Decimal("0.40")
        assert result.effective_rate < Decimal("0.55")
    
    def test_married_filing_separately(self):
        """Test married filing separately calculations."""
        income = IncomeBreakdown(
            w2_wages=Decimal("200000"),
        )
        
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_SEPARATELY,
            state="CA",
        )
        
        assert result.total_tax > Decimal("0")
        assert result.filing_status == FilingStatus.MARRIED_SEPARATELY


class TestEndToEndWorkflow:
    """
    Complete end-to-end workflow tests.
    """
    
    def test_annual_tax_planning_workflow(self):
        """Simulate annual tax planning session."""
        # 1. Import historical data
        fidelity_csv = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,DEPOSIT STOCK,TECH,RSU Vest,50,200.00,10000.00
01/15/2025,SALE,TECH,Same Day Sale,20,200.00,4000.00"""
        
        fidelity_result = parse_fidelity_csv(fidelity_csv)
        assert fidelity_result.success
        
        # 2. Build tax profile
        profile = TaxProfile(tax_year=2025)
        profile.w2_entries.append(W2Entry(
            employer_name="Tech Corp",
            wages=Decimal("300000"),
            federal_withheld=Decimal("60000"),
        ))
        
        # 3. Run red flag analysis
        report = analyze_red_flags(
            total_income=Decimal("310000"),
            total_tax_liability=Decimal("90000"),
            total_withheld=Decimal("60000"),
            rsu_income=Decimal("10000"),
            filing_status="single",
            state="CA",
        )
        
        # 4. Identify issues
        has_underwithholding = any(
            "withholding" in a.title.lower() for a in report.alerts
        )
        assert has_underwithholding
        
        # 5. Run what-if analysis
        engine = WhatIfEngine()
        baseline = ScenarioParameters(
            w2_wages=Decimal("300000"),
            rsu_income=Decimal("10000"),
            state_code="CA",
        )
        engine.set_baseline(baseline)
        
        # Model making estimated payment
        with_payment = ScenarioParameters(
            w2_wages=Decimal("300000"),
            rsu_income=Decimal("10000"),
            state_code="CA",
            federal_withheld=Decimal("60000"),  # Add withheld to balance
        )
        engine.add_scenario(with_payment)
        
        # 6. Get recommendations
        summary = engine.get_scenario_summary()
        assert summary["scenario_count"] == 2
