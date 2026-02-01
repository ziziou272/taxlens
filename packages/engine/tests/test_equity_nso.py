"""
Tests for NSO (Non-Qualified Stock Options) calculations.
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine.equity_nso import (
    NSOGrant,
    NSOExercise,
    NSOSale,
    calculate_nso_exercise,
    estimate_nso_withholding,
    nso_exercise_and_hold_example,
    nso_cashless_exercise_example,
)


class TestNSOExercise:
    """Tests for NSO exercise calculations."""
    
    def test_basic_exercise(self):
        """Test basic NSO exercise calculation."""
        exercise = calculate_nso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        assert exercise.shares_exercised == Decimal("1000")
        assert exercise.strike_price == Decimal("10")
        assert exercise.fmv_at_exercise == Decimal("50")
        
    def test_exercise_spread(self):
        """Test spread calculation."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
        )
        
        assert exercise.spread == Decimal("40")  # 50 - 10
        
    def test_ordinary_income(self):
        """Test ordinary income from NSO exercise."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
        )
        
        # Ordinary income = spread × shares = 40 × 1000 = 40,000
        assert exercise.ordinary_income == Decimal("40000.00")
        
    def test_total_cost(self):
        """Test cash required to exercise."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
        )
        
        # Cash to exercise = strike × shares = 10 × 1000 = 10,000
        assert exercise.total_cost == Decimal("10000.00")
        
    def test_cost_basis(self):
        """Test cost basis equals FMV at exercise."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
        )
        
        # Cost basis = FMV at exercise
        assert exercise.cost_basis_per_share == Decimal("50")
        
    def test_zero_spread(self):
        """Test when FMV equals strike (no income)."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("100"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("50"),
        )
        
        assert exercise.spread == Decimal("0")
        assert exercise.ordinary_income == Decimal("0.00")
        
    def test_underwater_options(self):
        """Test when FMV is below strike (underwater)."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("100"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("30"),  # Underwater
        )
        
        # Spread should be 0 (not negative)
        assert exercise.spread == Decimal("0")
        assert exercise.ordinary_income == Decimal("0.00")


class TestNSOSale:
    """Tests for NSO sale calculations."""
    
    def test_long_term_sale(self):
        """Test sale after 1+ year holding."""
        sale = NSOSale(
            sale_date=date(2026, 7, 1),
            shares_sold=Decimal("100"),
            sale_price=Decimal("60"),
            cost_basis_per_share=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        assert sale.is_long_term is True
        assert sale.holding_days >= 365
        
    def test_short_term_sale(self):
        """Test sale before 1 year holding."""
        sale = NSOSale(
            sale_date=date(2025, 9, 1),  # ~3 months later
            shares_sold=Decimal("100"),
            sale_price=Decimal("60"),
            cost_basis_per_share=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        assert sale.is_long_term is False
        assert sale.holding_days < 365
        
    def test_capital_gain(self):
        """Test capital gain calculation."""
        sale = NSOSale(
            sale_date=date(2026, 7, 1),
            shares_sold=Decimal("100"),
            sale_price=Decimal("60"),
            cost_basis_per_share=Decimal("50"),  # FMV at exercise
            exercise_date=date(2025, 6, 1),
        )
        
        # Gain = (60 - 50) × 100 = 1,000
        assert sale.capital_gain == Decimal("1000.00")
        
    def test_capital_loss(self):
        """Test capital loss (sold below cost basis)."""
        sale = NSOSale(
            sale_date=date(2026, 7, 1),
            shares_sold=Decimal("100"),
            sale_price=Decimal("40"),  # Below cost basis
            cost_basis_per_share=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        # Loss = (40 - 50) × 100 = -1,000
        assert sale.capital_gain == Decimal("-1000.00")
        
    def test_proceeds(self):
        """Test sale proceeds calculation."""
        sale = NSOSale(
            sale_date=date(2026, 7, 1),
            shares_sold=Decimal("100"),
            sale_price=Decimal("60"),
            cost_basis_per_share=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        assert sale.proceeds == Decimal("6000.00")


class TestNSOWithholding:
    """Tests for NSO withholding estimates."""
    
    def test_standard_withholding(self):
        """Test standard supplemental wage withholding."""
        withholding = estimate_nso_withholding(Decimal("40000"))
        
        # Federal: 22%
        assert withholding["federal"] == Decimal("8800.00")
        
        # State (CA): 10.23%
        assert withholding["state"] == Decimal("4092.00")
        
        # Social Security: 6.2%
        assert withholding["social_security"] == Decimal("2480.00")
        
        # Medicare: 1.45%
        assert withholding["medicare"] == Decimal("580.00")
        
    def test_over_ss_limit(self):
        """Test when over Social Security limit."""
        withholding = estimate_nso_withholding(
            Decimal("40000"),
            over_ss_limit=True,
        )
        
        # No Social Security withholding
        assert withholding["social_security"] == Decimal("0")
        
    def test_effective_rate(self):
        """Test effective withholding rate calculation."""
        withholding = estimate_nso_withholding(Decimal("100000"))
        
        # Total = 22% + 10.23% + 6.2% + 1.45% = 39.88%
        expected_total = Decimal("39880.00")
        assert withholding["total"] == expected_total
        assert withholding["effective_rate"] == Decimal("0.3988")
        
    def test_zero_income(self):
        """Test withholding on zero income."""
        withholding = estimate_nso_withholding(Decimal("0"))
        
        assert withholding["total"] == Decimal("0")
        assert withholding["effective_rate"] == Decimal("0")


class TestNSOExamples:
    """Test the example scenarios."""
    
    def test_exercise_and_hold_example(self):
        """Test exercise and hold scenario."""
        result = nso_exercise_and_hold_example()
        
        assert result["shares"] == Decimal("1000")
        assert result["strike_price"] == Decimal("10")
        assert result["fmv_at_exercise"] == Decimal("50")
        
        # Cash to exercise: 10 × 1000 = 10,000
        assert result["cash_to_exercise"] == Decimal("10000.00")
        
        # Ordinary income: 40 × 1000 = 40,000
        assert result["ordinary_income"] == Decimal("40000.00")
        
        # Cost basis per share = FMV
        assert result["cost_basis"] == Decimal("50")
        
    def test_cashless_exercise_example(self):
        """Test cashless (sell to cover) scenario."""
        result = nso_cashless_exercise_example()
        
        assert result["shares"] == Decimal("1000")
        assert result["ordinary_income"] == Decimal("40000.00")
        
        # Sold immediately at same price = no capital gain
        assert result["capital_gain"] == Decimal("0.00")
        
        # Gross proceeds = 50 × 1000 = 50,000
        assert result["gross_proceeds"] == Decimal("50000.00")


class TestNSOGrant:
    """Tests for NSO grant dataclass."""
    
    def test_grant_creation(self):
        """Test creating an NSO grant."""
        grant = NSOGrant(
            grant_date=date(2024, 1, 15),
            shares_granted=Decimal("5000"),
            strike_price=Decimal("25.00"),
            vesting_schedule="4 year, 1 year cliff",
            expiration_date=date(2034, 1, 15),
        )
        
        assert grant.shares_granted == Decimal("5000")
        assert grant.strike_price == Decimal("25.00")
        assert grant.expiration_date == date(2034, 1, 15)


class TestNSOEdgeCases:
    """Edge case tests."""
    
    def test_fractional_shares(self):
        """Test handling fractional shares."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("100.5"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
        )
        
        # Ordinary income = 40 × 100.5 = 4,020
        assert exercise.ordinary_income == Decimal("4020.00")
        
    def test_penny_prices(self):
        """Test with penny stock prices."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("10000"),
            strike_price=Decimal("0.01"),
            fmv_at_exercise=Decimal("0.10"),
        )
        
        # Spread = 0.09 × 10000 = 900
        assert exercise.ordinary_income == Decimal("900.00")
        
    def test_high_value_exercise(self):
        """Test high-value NSO exercise."""
        exercise = NSOExercise(
            exercise_date=date(2025, 6, 1),
            shares_exercised=Decimal("50000"),
            strike_price=Decimal("5"),
            fmv_at_exercise=Decimal("500"),
        )
        
        # Ordinary income = 495 × 50,000 = 24,750,000
        assert exercise.ordinary_income == Decimal("24750000.00")
        
        # With high income, federal withholding at 37% for over $1M
        withholding = estimate_nso_withholding(
            exercise.ordinary_income,
            federal_supplemental_rate=Decimal("0.37"),  # Over $1M rate
            over_ss_limit=True,
        )
        assert withholding["federal"] == Decimal("9157500.00")
