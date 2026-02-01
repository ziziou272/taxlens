"""
Tests for ISO (Incentive Stock Options) calculations.

Tests cover:
- Exercise calculations and AMT adjustment
- Qualifying vs disqualifying dispositions
- Ordinary income calculation for disqualifying
- Capital gains treatment
- AMT estimation
"""

from decimal import Decimal
from datetime import date
import pytest

from taxlens_engine.equity_iso import (
    ISOGrant,
    ISOExercise,
    ISOSale,
    ISODispositionType,
    calculate_iso_exercise,
    calculate_iso_sale,
    estimate_amt_impact,
    analyze_iso_scenario,
    iso_qualifying_disposition_example,
    iso_disqualifying_disposition_example,
    iso_underwater_sale_example,
)


class TestISOExercise:
    """Test ISO exercise calculations."""
    
    def test_basic_exercise(self):
        """Basic ISO exercise with bargain element."""
        exercise = calculate_iso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2023, 1, 1),
            exercise_date=date(2024, 6, 1),
        )
        
        # No regular income at exercise
        assert exercise.regular_tax_income == Decimal("0")
        
        # Bargain element = (50 - 10) * 1000 = $40,000
        assert exercise.bargain_element == Decimal("40000.00")
        
        # AMT adjustment = bargain element
        assert exercise.amt_adjustment == Decimal("40000.00")
        
        # Cost basis
        assert exercise.cost_basis_regular == Decimal("10")
        assert exercise.cost_basis_amt == Decimal("50")
    
    def test_exercise_no_spread(self):
        """Exercise when FMV equals strike (no bargain element)."""
        exercise = calculate_iso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2023, 1, 1),
            exercise_date=date(2024, 6, 1),
        )
        
        assert exercise.bargain_element == Decimal("0")
        assert exercise.amt_adjustment == Decimal("0")
    
    def test_exercise_underwater(self):
        """Exercise when FMV is below strike (underwater)."""
        exercise = calculate_iso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("30"),  # Below strike
            grant_date=date(2023, 1, 1),
            exercise_date=date(2024, 6, 1),
        )
        
        # No bargain element if underwater
        assert exercise.bargain_element == Decimal("0")
        
        # Still no regular income
        assert exercise.regular_tax_income == Decimal("0")
    
    def test_exercise_total_cost(self):
        """Calculate cash needed to exercise."""
        exercise = calculate_iso_exercise(
            shares=Decimal("500"),
            strike_price=Decimal("20"),
            fmv_at_exercise=Decimal("100"),
            grant_date=date(2023, 1, 1),
            exercise_date=date(2024, 6, 1),
        )
        
        # Total cost = 500 * $20 = $10,000
        assert exercise.total_cost == Decimal("10000.00")


class TestISODispositionType:
    """Test qualifying vs disqualifying disposition determination."""
    
    def test_qualifying_disposition(self):
        """Sale meets both holding requirements."""
        sale = calculate_iso_sale(
            shares=Decimal("100"),
            sale_price=Decimal("100"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2022, 1, 1),
            exercise_date=date(2023, 6, 1),
            sale_date=date(2025, 1, 1),  # > 2 yrs from grant, > 1 yr from exercise
        )
        
        assert sale.disposition_type == ISODispositionType.QUALIFYING
        assert sale.is_qualifying is True
    
    def test_disqualifying_short_hold_from_exercise(self):
        """Disqualifying: < 1 year from exercise."""
        sale = calculate_iso_sale(
            shares=Decimal("100"),
            sale_price=Decimal("100"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2022, 1, 1),
            exercise_date=date(2024, 6, 1),
            sale_date=date(2025, 1, 1),  # < 1 yr from exercise
        )
        
        assert sale.disposition_type == ISODispositionType.DISQUALIFYING
        assert sale.is_qualifying is False
    
    def test_disqualifying_short_hold_from_grant(self):
        """Disqualifying: < 2 years from grant."""
        sale = calculate_iso_sale(
            shares=Decimal("100"),
            sale_price=Decimal("100"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2024, 1, 1),
            exercise_date=date(2024, 2, 1),
            sale_date=date(2025, 6, 1),  # > 1 yr from exercise but < 2 yrs from grant
        )
        
        assert sale.disposition_type == ISODispositionType.DISQUALIFYING
    
    def test_boundary_exactly_one_year(self):
        """Exactly 365 days from exercise is qualifying (for that requirement)."""
        sale = calculate_iso_sale(
            shares=Decimal("100"),
            sale_price=Decimal("100"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2022, 1, 1),  # Need > 2 years
            exercise_date=date(2023, 6, 1),
            sale_date=date(2024, 6, 1),  # Exactly 365 days - NOT qualifying (need >365)
        )
        
        # 365 days is NOT > 365, so disqualifying
        assert sale.disposition_type == ISODispositionType.DISQUALIFYING
    
    def test_boundary_366_days(self):
        """366 days from exercise passes that requirement."""
        sale = calculate_iso_sale(
            shares=Decimal("100"),
            sale_price=Decimal("100"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2022, 1, 1),  # > 2 years
            exercise_date=date(2023, 6, 1),
            sale_date=date(2024, 6, 2),  # 366 days
        )
        
        assert sale.disposition_type == ISODispositionType.QUALIFYING


class TestQualifyingDisposition:
    """Test tax treatment for qualifying dispositions."""
    
    def test_all_gain_is_ltcg(self):
        """Qualifying: all gain is long-term capital gain."""
        sale = calculate_iso_sale(
            shares=Decimal("1000"),
            sale_price=Decimal("100"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2022, 1, 1),
            exercise_date=date(2023, 6, 1),
            sale_date=date(2025, 1, 1),
        )
        
        # No ordinary income
        assert sale.ordinary_income == Decimal("0")
        
        # All gain is capital gain
        # Gain = (100 - 10) * 1000 = $90,000
        assert sale.capital_gain == Decimal("90000.00")
        assert sale.is_long_term_capital_gain is True
    
    def test_qualifying_sale_at_loss(self):
        """Qualifying disposition at a loss."""
        sale = calculate_iso_sale(
            shares=Decimal("1000"),
            sale_price=Decimal("5"),  # Below strike!
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2022, 1, 1),
            exercise_date=date(2023, 6, 1),
            sale_date=date(2025, 1, 1),
        )
        
        assert sale.is_qualifying is True
        assert sale.ordinary_income == Decimal("0")
        
        # Capital loss = (5 - 10) * 1000 = -$5,000
        assert sale.capital_gain == Decimal("-5000.00")


class TestDisqualifyingDisposition:
    """Test tax treatment for disqualifying dispositions."""
    
    def test_ordinary_income_equals_bargain(self):
        """Disqualifying: ordinary income = bargain element when gain > bargain."""
        sale = calculate_iso_sale(
            shares=Decimal("1000"),
            sale_price=Decimal("80"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),  # Bargain = $40,000
            grant_date=date(2024, 1, 1),
            exercise_date=date(2024, 7, 1),
            sale_date=date(2025, 1, 1),  # < 1 year
        )
        
        assert sale.is_qualifying is False
        
        # Ordinary income = bargain element = $40,000
        assert sale.ordinary_income == Decimal("40000.00")
        
        # Remaining gain is capital gain
        # Total gain = (80-10) * 1000 = $70,000
        # Capital gain = 70,000 - 40,000 = $30,000
        assert sale.capital_gain == Decimal("30000.00")
    
    def test_ordinary_income_limited_by_actual_gain(self):
        """Disqualifying: ordinary income limited when stock dropped."""
        sale = calculate_iso_sale(
            shares=Decimal("1000"),
            sale_price=Decimal("30"),  # Dropped from $50 FMV
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),  # Bargain would be $40,000
            grant_date=date(2024, 1, 1),
            exercise_date=date(2024, 7, 1),
            sale_date=date(2025, 1, 1),
        )
        
        # Actual gain = (30 - 10) * 1000 = $20,000
        # Ordinary income limited to actual gain
        assert sale.ordinary_income == Decimal("20000.00")
        
        # No additional capital gain
        assert sale.capital_gain == Decimal("0.00")
    
    def test_disqualifying_sale_at_loss(self):
        """Disqualifying disposition at actual loss."""
        sale = calculate_iso_sale(
            shares=Decimal("1000"),
            sale_price=Decimal("5"),  # Below strike
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2024, 1, 1),
            exercise_date=date(2024, 7, 1),
            sale_date=date(2025, 1, 1),
        )
        
        # No ordinary income (actual loss)
        assert sale.ordinary_income == Decimal("0")
        
        # Capital loss
        assert sale.capital_gain == Decimal("-5000.00")
    
    def test_disqualifying_holding_period_ltcg(self):
        """Disqualifying disposition can still have LTCG if held > 1 year from exercise."""
        sale = calculate_iso_sale(
            shares=Decimal("1000"),
            sale_price=Decimal("80"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            grant_date=date(2023, 6, 1),  # < 2 years from sale
            exercise_date=date(2023, 7, 1),  # > 1 year from sale
            sale_date=date(2024, 8, 1),
        )
        
        # Disqualifying (< 2 years from grant)
        assert sale.is_qualifying is False
        
        # But capital gain is long-term (> 1 year from exercise)
        assert sale.is_long_term_capital_gain is True


class TestAMTEstimation:
    """Test AMT impact estimation."""
    
    def test_low_income_no_amt(self):
        """Low income may not trigger AMT."""
        result = estimate_amt_impact(
            bargain_element=Decimal("20000"),
            regular_taxable_income=Decimal("80000"),
            filing_status="single",
        )
        
        assert "estimated_amt_owed" in result
        assert result["bargain_element"] == Decimal("20000")
    
    def test_high_bargain_element(self):
        """Large bargain element likely triggers AMT."""
        result = estimate_amt_impact(
            bargain_element=Decimal("200000"),
            regular_taxable_income=Decimal("200000"),
            filing_status="single",
        )
        
        # Should have some AMT
        assert result["amt_income"] > result["bargain_element"]
        assert result["estimated_amt_owed"] >= Decimal("0")
    
    def test_married_filing_jointly(self):
        """MFJ has higher exemption."""
        single_result = estimate_amt_impact(
            bargain_element=Decimal("100000"),
            regular_taxable_income=Decimal("200000"),
            filing_status="single",
        )
        
        mfj_result = estimate_amt_impact(
            bargain_element=Decimal("100000"),
            regular_taxable_income=Decimal("200000"),
            filing_status="married_jointly",
        )
        
        # MFJ should have higher exemption
        assert mfj_result["amt_exemption"] > single_result["amt_exemption"]


class TestISOAnalysis:
    """Test complete ISO scenario analysis."""
    
    def test_analyze_qualifying(self):
        """Analyze qualifying disposition scenario."""
        summary = analyze_iso_scenario(
            shares=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            sale_price=Decimal("100"),
            grant_date=date(2022, 1, 1),
            exercise_date=date(2023, 6, 1),
            sale_date=date(2025, 1, 1),
        )
        
        assert summary.disposition_type == ISODispositionType.QUALIFYING
        assert summary.ordinary_income == Decimal("0")
        assert summary.capital_gain == Decimal("90000.00")
        assert summary.is_long_term is True
        assert summary.total_gain == Decimal("90000.00")
    
    def test_analyze_disqualifying(self):
        """Analyze disqualifying disposition scenario."""
        summary = analyze_iso_scenario(
            shares=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            sale_price=Decimal("80"),
            grant_date=date(2024, 1, 1),
            exercise_date=date(2024, 7, 1),
            sale_date=date(2025, 1, 1),
        )
        
        assert summary.disposition_type == ISODispositionType.DISQUALIFYING
        assert summary.ordinary_income == Decimal("40000.00")
        assert summary.capital_gain == Decimal("30000.00")


class TestExamples:
    """Test built-in example scenarios."""
    
    def test_qualifying_example(self):
        """Test qualifying disposition example."""
        result = iso_qualifying_disposition_example()
        
        assert result["disposition_type"] == "qualifying"
        assert result["ordinary_income"] == Decimal("0")
        assert result["is_long_term"] is True
        assert result["capital_gain"] == Decimal("90000.00")
    
    def test_disqualifying_example(self):
        """Test disqualifying disposition example."""
        result = iso_disqualifying_disposition_example()
        
        assert result["disposition_type"] == "disqualifying"
        assert result["ordinary_income"] == Decimal("40000.00")
        assert result["capital_gain"] == Decimal("30000.00")
    
    def test_underwater_example(self):
        """Test underwater sale example."""
        result = iso_underwater_sale_example()
        
        assert result["disposition_type"] == "disqualifying"
        # Ordinary income limited to actual gain
        assert result["ordinary_income"] == Decimal("20000.00")
        # No additional capital gain
        assert result["capital_gain"] == Decimal("0.00")
        # Total gain
        assert result["total_gain"] == Decimal("20000.00")


class TestISOGrant:
    """Test ISOGrant helper class."""
    
    def test_shares_available(self):
        """Test tracking available shares."""
        grant = ISOGrant(
            grant_date=date(2023, 1, 1),
            shares_granted=Decimal("10000"),
            strike_price=Decimal("10"),
        )
        
        assert grant.shares_available_to_exercise() == Decimal("10000")
        assert grant.shares_available_to_exercise(Decimal("3000")) == Decimal("7000")
