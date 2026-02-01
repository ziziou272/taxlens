"""
Tests for federal tax calculations.

These tests verify accuracy against known tax scenarios.
"""

from decimal import Decimal
import pytest

from taxlens_engine.federal import (
    calculate_federal_tax,
    calculate_ltcg_tax,
    calculate_fica,
    calculate_niit,
    get_marginal_rate,
)
from taxlens_engine.models import FilingStatus


class TestFederalTaxBrackets:
    """Test federal income tax bracket calculations."""
    
    def test_zero_income(self):
        """Zero income should have zero tax."""
        tax = calculate_federal_tax(Decimal("0"), FilingStatus.SINGLE)
        assert tax == Decimal("0")
    
    def test_negative_income(self):
        """Negative income should have zero tax."""
        tax = calculate_federal_tax(Decimal("-10000"), FilingStatus.SINGLE)
        assert tax == Decimal("0")
    
    def test_single_first_bracket_only(self):
        """Single filer in 10% bracket only."""
        # $10,000 income = $10,000 * 10% = $1,000
        tax = calculate_federal_tax(Decimal("10000"), FilingStatus.SINGLE)
        assert tax == Decimal("1000.00")
    
    def test_single_two_brackets(self):
        """Single filer spanning 10% and 12% brackets."""
        # $30,000 income:
        # - First $11,925 at 10% = $1,192.50
        # - Next $18,075 at 12% = $2,169.00
        # - Total = $3,361.50
        tax = calculate_federal_tax(Decimal("30000"), FilingStatus.SINGLE)
        assert tax == Decimal("3361.50")
    
    def test_single_high_income(self):
        """Single filer with $300K income (hitting 35% bracket)."""
        # Complex calculation - verify it's in reasonable range
        tax = calculate_federal_tax(Decimal("300000"), FilingStatus.SINGLE)
        assert tax > Decimal("60000")  # Should be substantial
        assert tax < Decimal("120000")  # But not over 40% effective
    
    def test_married_jointly_double_brackets(self):
        """Married filing jointly has double-width brackets."""
        # MFJ at $60,000 should be lower than single at $60,000
        tax_single = calculate_federal_tax(Decimal("60000"), FilingStatus.SINGLE)
        tax_mfj = calculate_federal_tax(Decimal("60000"), FilingStatus.MARRIED_JOINTLY)
        assert tax_mfj < tax_single
    
    def test_tech_employee_scenario(self):
        """Typical tech employee: $200K W-2 + $100K RSU."""
        # $300,000 taxable income, married filing jointly
        tax = calculate_federal_tax(Decimal("300000"), FilingStatus.MARRIED_JOINTLY)
        # Expected to be in 24-32% effective range
        effective_rate = tax / Decimal("300000")
        assert Decimal("0.20") < effective_rate < Decimal("0.30")


class TestLTCGTax:
    """Test long-term capital gains tax calculations."""
    
    def test_zero_gains(self):
        """Zero gains should have zero tax."""
        tax = calculate_ltcg_tax(Decimal("0"), Decimal("50000"), FilingStatus.SINGLE)
        assert tax == Decimal("0")
    
    def test_gains_in_zero_bracket(self):
        """Low income keeps gains in 0% bracket."""
        # Single with $30K ordinary income + $10K LTCG
        # $30K + $10K = $40K, still under $48,350 threshold
        tax = calculate_ltcg_tax(
            Decimal("10000"),
            Decimal("30000"),
            FilingStatus.SINGLE,
        )
        assert tax == Decimal("0.00")
    
    def test_gains_span_brackets(self):
        """Gains that span 0% and 15% brackets."""
        # Single with $45K ordinary + $10K LTCG
        # $45K ordinary puts us close to threshold
        # Some gains at 0%, some at 15%
        tax = calculate_ltcg_tax(
            Decimal("10000"),
            Decimal("45000"),
            FilingStatus.SINGLE,
        )
        assert tax > Decimal("0")
        assert tax < Decimal("1500")  # Less than 15% of gains
    
    def test_high_income_all_at_20(self):
        """High income pushes all gains to 20% bracket."""
        # Single with $600K ordinary income
        tax = calculate_ltcg_tax(
            Decimal("100000"),
            Decimal("600000"),
            FilingStatus.SINGLE,
        )
        # All gains at 20%
        assert tax == Decimal("20000.00")


class TestMarginalRate:
    """Test marginal rate lookups."""
    
    def test_first_bracket(self):
        """Income in first bracket should be 10%."""
        rate = get_marginal_rate(Decimal("10000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.10")
    
    def test_top_bracket(self):
        """High income should be in 37% bracket."""
        rate = get_marginal_rate(Decimal("700000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.37")
    
    def test_24_percent_bracket(self):
        """$150K single should be in 24% bracket."""
        rate = get_marginal_rate(Decimal("150000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.24")


class TestFICA:
    """Test Social Security and Medicare calculations."""
    
    def test_below_ss_wage_base(self):
        """Wages below SS wage base get full SS tax."""
        ss, medicare, additional = calculate_fica(
            Decimal("100000"),
            FilingStatus.SINGLE,
        )
        assert ss == Decimal("6200.00")  # 6.2% of $100K
        assert medicare == Decimal("1450.00")  # 1.45% of $100K
        assert additional == Decimal("0")  # Below threshold
    
    def test_above_ss_wage_base(self):
        """Wages above SS wage base are capped."""
        ss, medicare, additional = calculate_fica(
            Decimal("200000"),
            FilingStatus.SINGLE,
        )
        # SS capped at wage base ($176,100 in 2025)
        assert ss == Decimal("10918.20")  # 6.2% of $176,100
        # Medicare on full amount
        assert medicare == Decimal("2900.00")  # 1.45% of $200K
        # Additional Medicare on amount over $200K (single)
        assert additional == Decimal("0")  # At exactly threshold
    
    def test_additional_medicare(self):
        """Wages over $200K (single) trigger additional Medicare."""
        ss, medicare, additional = calculate_fica(
            Decimal("300000"),
            FilingStatus.SINGLE,
        )
        # Additional Medicare: 0.9% on $100K over threshold
        assert additional == Decimal("900.00")


class TestNIIT:
    """Test Net Investment Income Tax calculations."""
    
    def test_below_threshold(self):
        """MAGI below threshold should have no NIIT."""
        niit = calculate_niit(
            Decimal("50000"),  # Investment income
            Decimal("150000"),  # MAGI
            FilingStatus.SINGLE,
        )
        assert niit == Decimal("0")
    
    def test_above_threshold_investment_smaller(self):
        """NIIT on lesser of investment income or excess MAGI."""
        # MAGI $250K (single), threshold $200K, excess $50K
        # Investment income $30K
        # NIIT on $30K (smaller of $30K and $50K)
        niit = calculate_niit(
            Decimal("30000"),
            Decimal("250000"),
            FilingStatus.SINGLE,
        )
        assert niit == Decimal("1140.00")  # 3.8% of $30K
    
    def test_above_threshold_excess_smaller(self):
        """NIIT when excess MAGI is smaller than investment income."""
        # MAGI $220K (single), threshold $200K, excess $20K
        # Investment income $50K
        # NIIT on $20K (smaller of $50K and $20K)
        niit = calculate_niit(
            Decimal("50000"),
            Decimal("220000"),
            FilingStatus.SINGLE,
        )
        assert niit == Decimal("760.00")  # 3.8% of $20K
