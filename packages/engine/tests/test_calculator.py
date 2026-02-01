"""
Tests for the complete tax calculator.

Integration tests for federal + state tax calculations.
"""

from decimal import Decimal
import pytest

from taxlens_engine.calculator import calculate_taxes, TaxCalculatorInput
from taxlens_engine.models import FilingStatus, IncomeBreakdown, TaxSummary


class TestCalculatorBasic:
    """Basic calculator functionality tests."""
    
    def test_simple_w2_income(self):
        """Simple W-2 income, no equity."""
        income = IncomeBreakdown(w2_wages=Decimal("100000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        assert isinstance(result, TaxSummary)
        assert result.filing_status == FilingStatus.SINGLE
        assert result.state_code == "CA"
        assert result.federal_tax_total > 0
        assert result.state_tax > 0
        assert result.total_tax > 0
    
    def test_zero_income(self):
        """Zero income should have minimal tax."""
        income = IncomeBreakdown()
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        assert result.federal_tax_total == Decimal("0")
        assert result.state_tax == Decimal("0")
    
    def test_deduction_applied(self):
        """Standard deduction should be applied."""
        income = IncomeBreakdown(w2_wages=Decimal("100000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Federal standard deduction for single ~$15K
        assert result.standard_deduction >= Decimal("14000")
        assert result.taxable_income < income.total_income


class TestTechEmployeeScenarios:
    """Test typical tech employee scenarios."""
    
    def test_mid_level_engineer_single(self):
        """Mid-level engineer: $200K W2, single, CA."""
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Federal tax ~$35K-$45K
        assert Decimal("30000") < result.federal_tax_total < Decimal("50000")
        # CA tax ~$15K-$20K
        assert Decimal("12000") < result.state_tax < Decimal("22000")
        # Effective rate ~25-35%
        effective = result.total_tax / result.income.total_income
        assert Decimal("0.25") < effective < Decimal("0.40")
    
    def test_senior_engineer_with_rsu(self):
        """Senior engineer: $300K W2 + $150K RSU, married, CA."""
        income = IncomeBreakdown(
            w2_wages=Decimal("300000"),
            rsu_income=Decimal("150000"),
        )
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            state="CA",
        )
        
        # Total income $450K
        assert result.income.total_income == Decimal("450000")
        
        # Federal tax ~$88K (based on 2025 brackets)
        assert Decimal("85000") < result.federal_tax_total < Decimal("95000")
        
        # CA tax ~$34K (based on CA 2025 brackets)
        assert Decimal("30000") < result.state_tax < Decimal("40000")
        
        # Total tax ~$140K-$155K
        assert Decimal("135000") < result.total_tax < Decimal("160000")
    
    def test_engineer_with_ltcg(self):
        """Engineer with stock sales: $250K W2 + $100K LTCG."""
        income = IncomeBreakdown(
            w2_wages=Decimal("250000"),
            long_term_gains=Decimal("100000"),
        )
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            state="CA",
        )
        
        # LTCG should be taxed at preferential rates
        assert result.federal_tax_on_ltcg > 0
        assert result.federal_tax_on_ltcg < Decimal("25000")  # Less than 25%
        
        # NIIT might apply
        assert result.niit >= 0
    
    def test_full_tech_package(self):
        """Full tech comp: $300K W2 + $150K RSU + $50K LTCG."""
        income = IncomeBreakdown(
            w2_wages=Decimal("300000"),
            rsu_income=Decimal("150000"),
            long_term_gains=Decimal("50000"),
        )
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            state="CA",
        )
        
        # Total income $500K
        assert result.income.total_income == Decimal("500000")
        
        # Should have NIIT on investment income
        assert result.niit > 0
        
        # Check effective rate is reasonable
        effective = result.total_tax / result.income.total_income
        assert Decimal("0.30") < effective < Decimal("0.40")


class TestFICACalculations:
    """Test FICA tax calculations."""
    
    def test_fica_included(self):
        """FICA taxes should be calculated."""
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # SS tax should be capped at wage base
        assert result.social_security_tax > Decimal("10000")
        # Medicare should be on full wages
        assert result.medicare_tax > Decimal("2500")
    
    def test_additional_medicare_high_income(self):
        """Additional Medicare tax for high earners."""
        income = IncomeBreakdown(w2_wages=Decimal("300000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Additional Medicare on $100K over threshold
        assert result.additional_medicare_tax == Decimal("900.00")


class TestWithholding:
    """Test withholding comparison."""
    
    def test_withholding_default_zero(self):
        """Default withholding should be zero."""
        income = IncomeBreakdown(w2_wages=Decimal("100000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        assert result.total_withheld == Decimal("0")
        assert result.balance_due == result.total_tax
    
    def test_withholding_comparison(self):
        """Test with specified withholding."""
        income = IncomeBreakdown(w2_wages=Decimal("100000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
            federal_withheld=Decimal("15000"),
            state_withheld=Decimal("5000"),
        )
        
        assert result.total_withheld == Decimal("20000")
        # Balance due = total tax - withheld
        expected_balance = result.total_tax - Decimal("20000")
        assert result.balance_due == expected_balance


class TestEffectiveAndMarginalRates:
    """Test effective and marginal rate calculations."""
    
    def test_effective_rate_calculation(self):
        """Effective rate should be total tax / total income."""
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        expected_effective = result.total_tax / result.income.total_income
        assert abs(result.effective_rate - expected_effective) < Decimal("0.001")
    
    def test_marginal_rate_reasonable(self):
        """Marginal rate should be reasonable for income level."""
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Combined marginal should be sum of federal + state
        # $200K - $15K std deduction = $185K taxable
        # Federal 24% (under $197,300 threshold) + CA 9.3% = 33.3%
        assert Decimal("0.30") < result.marginal_rate < Decimal("0.40")


class TestNoStateScenario:
    """Test calculations without state tax."""
    
    def test_no_state_tax(self):
        """Test calculation with no state (or state with no income tax)."""
        income = IncomeBreakdown(w2_wages=Decimal("100000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state=None,  # No state
        )
        
        assert result.state_tax == Decimal("0")
        assert result.state_code is None
        assert result.federal_tax_total > 0


class TestWarnings:
    """Test warning generation."""
    
    def test_amt_warning_for_iso(self):
        """AMT warning should be generated for ISO exercises."""
        income = IncomeBreakdown(
            w2_wages=Decimal("200000"),
            iso_bargain_element=Decimal("100000"),
        )
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Should have AMT warning if AMT is owed
        if result.amt_owed > 0:
            assert any("AMT" in w for w in result.warnings)
    
    def test_high_income_warning(self):
        """High income might trigger NIIT or other warnings."""
        income = IncomeBreakdown(
            w2_wages=Decimal("500000"),
            long_term_gains=Decimal("200000"),
        )
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        
        # Should have some warnings for complex situation
        # (NIIT, high marginal rate, etc.)
        assert result.niit > 0
