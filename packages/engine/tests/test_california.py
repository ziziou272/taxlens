"""
Tests for California state tax calculations.

These tests verify CA tax brackets, Mental Health Services Tax,
and SDI considerations.
"""

from decimal import Decimal
import pytest

from taxlens_engine.california import (
    calculate_california_tax,
    calculate_mental_health_tax,
    calculate_sdi,
    get_ca_standard_deduction,
    get_ca_marginal_rate,
    CA_BRACKETS_2025,
)
from taxlens_engine.models import FilingStatus


class TestCAStandardDeduction:
    """Test California standard deductions."""
    
    def test_single_deduction(self):
        """Single filer standard deduction."""
        deduction = get_ca_standard_deduction(FilingStatus.SINGLE)
        assert deduction == Decimal("5540")
    
    def test_married_jointly_deduction(self):
        """Married filing jointly standard deduction."""
        deduction = get_ca_standard_deduction(FilingStatus.MARRIED_JOINTLY)
        assert deduction == Decimal("11080")
    
    def test_head_of_household_deduction(self):
        """Head of household standard deduction."""
        deduction = get_ca_standard_deduction(FilingStatus.HEAD_OF_HOUSEHOLD)
        assert deduction == Decimal("11080")


class TestCATaxBrackets:
    """Test California income tax bracket calculations."""
    
    def test_zero_income(self):
        """Zero income should have zero tax."""
        tax = calculate_california_tax(Decimal("0"), FilingStatus.SINGLE)
        assert tax == Decimal("0")
    
    def test_negative_income(self):
        """Negative income should have zero tax."""
        tax = calculate_california_tax(Decimal("-10000"), FilingStatus.SINGLE)
        assert tax == Decimal("0")
    
    def test_single_first_bracket_only(self):
        """Single filer in 1% bracket only."""
        # $8,000 income = $8,000 * 1% = $80
        tax = calculate_california_tax(Decimal("8000"), FilingStatus.SINGLE)
        assert tax == Decimal("80.00")
    
    def test_single_moderate_income(self):
        """Single filer with moderate income."""
        # $50,000 taxable income - should span multiple brackets
        # CA brackets for 2025: 1%, 2%, 4%, 6% up to ~$56K
        tax = calculate_california_tax(Decimal("50000"), FilingStatus.SINGLE)
        # Expected ~$1,500-$2,000 (effective rate ~3-4%)
        assert tax > Decimal("1400")
        assert tax < Decimal("2500")
    
    def test_single_high_income(self):
        """Single filer with high income reaching 9.3% bracket."""
        # $100,000 taxable income
        tax = calculate_california_tax(Decimal("100000"), FilingStatus.SINGLE)
        # Expected effective rate around 6-8%
        effective_rate = tax / Decimal("100000")
        assert Decimal("0.05") < effective_rate < Decimal("0.10")
    
    def test_married_jointly_double_brackets(self):
        """Married filing jointly has double-width brackets."""
        tax_single = calculate_california_tax(Decimal("80000"), FilingStatus.SINGLE)
        tax_mfj = calculate_california_tax(Decimal("80000"), FilingStatus.MARRIED_JOINTLY)
        assert tax_mfj < tax_single
    
    def test_very_high_income_133_bracket(self):
        """Very high income reaches 12.3% and 13.3% brackets."""
        # $700,000 taxable income (single)
        tax = calculate_california_tax(Decimal("700000"), FilingStatus.SINGLE)
        # Top marginal rate is 12.3% (13.3% kicks in at $1M)
        effective_rate = tax / Decimal("700000")
        assert Decimal("0.09") < effective_rate < Decimal("0.13")
    
    def test_tech_employee_scenario_single(self):
        """Typical tech employee: $300K taxable, single."""
        tax = calculate_california_tax(Decimal("300000"), FilingStatus.SINGLE)
        # Expected ~$23K-$27K CA tax (effective rate ~8%)
        assert Decimal("22000") < tax < Decimal("28000")
    
    def test_tech_employee_scenario_married(self):
        """Typical tech employee: $420K taxable, married."""
        # $420K CA taxable income
        tax = calculate_california_tax(Decimal("420000"), FilingStatus.MARRIED_JOINTLY)
        # Expected ~$30K-$36K CA tax (effective rate ~7-8%)
        assert Decimal("28000") < tax < Decimal("38000")


class TestMentalHealthServicesTax:
    """Test Mental Health Services Tax (additional 1% over $1M)."""
    
    def test_below_threshold(self):
        """Income below $1M should have no MH tax."""
        mh_tax = calculate_mental_health_tax(Decimal("500000"))
        assert mh_tax == Decimal("0")
    
    def test_at_threshold(self):
        """Income exactly at $1M should have no MH tax."""
        mh_tax = calculate_mental_health_tax(Decimal("1000000"))
        assert mh_tax == Decimal("0")
    
    def test_above_threshold(self):
        """Income above $1M gets 1% on excess."""
        # $1.5M income = 1% on $500K = $5,000
        mh_tax = calculate_mental_health_tax(Decimal("1500000"))
        assert mh_tax == Decimal("5000.00")
    
    def test_significantly_above_threshold(self):
        """Income significantly above $1M."""
        # $3M income = 1% on $2M = $20,000
        mh_tax = calculate_mental_health_tax(Decimal("3000000"))
        assert mh_tax == Decimal("20000.00")


class TestSDI:
    """Test California State Disability Insurance."""
    
    def test_below_wage_limit(self):
        """Wages below SDI limit."""
        # SDI rate is 1.1% in 2025, wage limit ~$153,164
        sdi = calculate_sdi(Decimal("100000"))
        assert sdi == Decimal("1100.00")  # 1.1% of $100K
    
    def test_above_wage_limit(self):
        """Wages above SDI limit should be capped."""
        sdi = calculate_sdi(Decimal("200000"))
        # Capped at wage limit
        assert sdi == Decimal("1684.80")  # 1.1% of $153,164


class TestCAMarginalRate:
    """Test California marginal rate lookups."""
    
    def test_first_bracket(self):
        """Income in first bracket should be 1%."""
        rate = get_ca_marginal_rate(Decimal("8000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.01")
    
    def test_highest_regular_bracket(self):
        """High income (under $1M) should be 12.3%."""
        rate = get_ca_marginal_rate(Decimal("800000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.123")
    
    def test_mental_health_bracket(self):
        """Income over $1M should be 13.3%."""
        rate = get_ca_marginal_rate(Decimal("1500000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.133")
    
    def test_middle_bracket(self):
        """$100K single should be in 9.3% bracket."""
        rate = get_ca_marginal_rate(Decimal("100000"), FilingStatus.SINGLE)
        assert rate == Decimal("0.093")
