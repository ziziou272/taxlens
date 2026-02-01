"""
Tests for RSU (Restricted Stock Units) calculations.

Tests cover:
- RSU vesting and ordinary income
- RSU sale and capital gains
- Withholding calculations
- Common scenarios
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine.equity_rsu import (
    RSUGrant,
    RSUVesting,
    RSUSale,
    RSUWithholding,
    calculate_rsu_withholding,
    calculate_rsu_vesting,
    calculate_rsu_sale,
    analyze_rsu_scenario,
    rsu_same_day_sale_example,
    rsu_hold_and_sell_higher_example,
    rsu_hold_and_sell_lower_example,
    FEDERAL_SUPPLEMENTAL_RATE,
    CA_SUPPLEMENTAL_RATE,
    SOCIAL_SECURITY_RATE,
    MEDICARE_RATE,
)


class TestRSUGrant:
    """Tests for RSUGrant dataclass."""
    
    def test_grant_creation(self):
        grant = RSUGrant(
            grant_date=date(2024, 1, 15),
            total_shares=Decimal("1000"),
            company="ACME Corp",
        )
        assert grant.total_shares == Decimal("1000")
        assert grant.company == "ACME Corp"
    
    def test_shares_remaining(self):
        grant = RSUGrant(
            grant_date=date(2024, 1, 15),
            total_shares=Decimal("1000"),
        )
        assert grant.shares_remaining(Decimal("250")) == Decimal("750")
        assert grant.shares_remaining(Decimal("1000")) == Decimal("0")
        # Can't go negative
        assert grant.shares_remaining(Decimal("1200")) == Decimal("0")


class TestRSUVesting:
    """Tests for RSU vesting events."""
    
    def test_gross_income(self):
        """FMV × shares = ordinary income."""
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vesting=Decimal("150.00"),
        )
        assert vesting.gross_income == Decimal("15000.00")
    
    def test_cost_basis(self):
        """Cost basis = FMV at vesting."""
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vesting=Decimal("150.00"),
        )
        assert vesting.cost_basis_per_share == Decimal("150.00")
        assert vesting.total_cost_basis == Decimal("15000.00")
    
    def test_net_shares_after_withholding(self):
        """Net shares = vested - withheld."""
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vesting=Decimal("150.00"),
            shares_withheld_for_taxes=Decimal("40"),
        )
        assert vesting.net_shares == Decimal("60")
    
    def test_fractional_shares(self):
        """Handle fractional share amounts."""
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("100.5"),
            fmv_at_vesting=Decimal("99.99"),
        )
        # 100.5 * 99.99 = 10048.995 → rounds to 10049.00
        assert vesting.gross_income == Decimal("10049.00")


class TestRSUSale:
    """Tests for RSU sale calculations."""
    
    def test_capital_gain(self):
        """Gain = (Sale Price - Cost Basis) × Shares."""
        sale = RSUSale(
            sale_date=date(2025, 6, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("200.00"),
            cost_basis_per_share=Decimal("150.00"),
            vesting_date=date(2025, 3, 15),
        )
        assert sale.capital_gain == Decimal("5000.00")
        assert sale.proceeds == Decimal("20000.00")
        assert sale.total_cost_basis == Decimal("15000.00")
    
    def test_capital_loss(self):
        """Handle capital loss (stock went down)."""
        sale = RSUSale(
            sale_date=date(2025, 6, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("100.00"),
            cost_basis_per_share=Decimal("150.00"),
            vesting_date=date(2025, 3, 15),
        )
        assert sale.capital_gain == Decimal("-5000.00")
    
    def test_same_day_sale_zero_gain(self):
        """Same-day sale has zero capital gain."""
        sale = RSUSale(
            sale_date=date(2025, 3, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("150.00"),
            cost_basis_per_share=Decimal("150.00"),
            vesting_date=date(2025, 3, 15),
        )
        assert sale.capital_gain == Decimal("0.00")
    
    def test_short_term_holding(self):
        """< 1 year = short-term."""
        sale = RSUSale(
            sale_date=date(2025, 6, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("200.00"),
            cost_basis_per_share=Decimal("150.00"),
            vesting_date=date(2025, 3, 15),  # 3 months ago
        )
        assert sale.is_long_term is False
        assert sale.gain_type == "short_term"
    
    def test_long_term_holding(self):
        """> 1 year = long-term."""
        sale = RSUSale(
            sale_date=date(2026, 6, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("200.00"),
            cost_basis_per_share=Decimal("150.00"),
            vesting_date=date(2025, 3, 15),  # ~15 months ago
        )
        assert sale.is_long_term is True
        assert sale.gain_type == "long_term"
    
    def test_exactly_one_year(self):
        """Exactly 365 days is NOT long-term (must be >365)."""
        sale = RSUSale(
            sale_date=date(2026, 3, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("200.00"),
            cost_basis_per_share=Decimal("150.00"),
            vesting_date=date(2025, 3, 15),  # Exactly 365 days
        )
        assert sale.holding_period_days == 365
        assert sale.is_long_term is False  # Must be > 365


class TestRSUWithholding:
    """Tests for RSU withholding calculations."""
    
    def test_federal_supplemental_rate(self):
        """Federal supplemental rate is 22%."""
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("10000"),
            state="CA",
        )
        expected_federal = Decimal("10000") * FEDERAL_SUPPLEMENTAL_RATE
        assert withholding.federal_withholding == expected_federal.quantize(Decimal("0.01"))
    
    def test_ca_state_rate(self):
        """California supplemental rate is 10.23%."""
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("10000"),
            state="CA",
        )
        expected_state = Decimal("10000") * CA_SUPPLEMENTAL_RATE
        assert withholding.state_withholding == expected_state.quantize(Decimal("0.01"))
    
    def test_social_security_under_wage_base(self):
        """SS applies up to wage base."""
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("10000"),
            ytd_wages=Decimal("0"),
        )
        expected_ss = Decimal("10000") * SOCIAL_SECURITY_RATE
        assert withholding.social_security == expected_ss.quantize(Decimal("0.01"))
    
    def test_social_security_over_wage_base(self):
        """No SS when already over wage base."""
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("10000"),
            ytd_wages=Decimal("200000"),  # Over wage base
        )
        assert withholding.social_security == Decimal("0.00")
    
    def test_social_security_partial_over_wage_base(self):
        """Partial SS when vesting pushes over wage base."""
        # Wage base is $176,100 in 2025
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("10000"),
            ytd_wages=Decimal("170000"),  # $6,100 room left
        )
        expected_ss = Decimal("6100") * SOCIAL_SECURITY_RATE
        assert withholding.social_security == expected_ss.quantize(Decimal("0.01"))
    
    def test_medicare_on_all_income(self):
        """Medicare applies to all income (no cap)."""
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("100000"),
            ytd_wages=Decimal("500000"),
        )
        expected_medicare = Decimal("100000") * MEDICARE_RATE
        assert withholding.medicare == expected_medicare.quantize(Decimal("0.01"))
    
    def test_additional_medicare(self):
        """Additional Medicare applies over threshold."""
        # Single threshold is $200k
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("50000"),
            ytd_wages=Decimal("180000"),  # $20k over when this vests
            filing_status="single",
        )
        # Additional Medicare on $30k ($180k + $50k - $200k = $30k)
        expected_additional = Decimal("30000") * Decimal("0.009")
        assert withholding.additional_medicare == expected_additional.quantize(Decimal("0.01"))
    
    def test_total_withholding(self):
        """Total withholding sums all components."""
        withholding = RSUWithholding(
            gross_income=Decimal("10000"),
            federal_withholding=Decimal("2200"),
            state_withholding=Decimal("1023"),
            social_security=Decimal("620"),
            medicare=Decimal("145"),
            additional_medicare=Decimal("0"),
        )
        assert withholding.total_withholding == Decimal("3988.00")
    
    def test_effective_rate(self):
        """Effective rate = total / gross."""
        withholding = RSUWithholding(
            gross_income=Decimal("10000"),
            federal_withholding=Decimal("2200"),
            state_withholding=Decimal("1023"),
            social_security=Decimal("620"),
            medicare=Decimal("145"),
            additional_medicare=Decimal("0"),
        )
        assert withholding.effective_withholding_rate == Decimal("0.3988")
    
    def test_high_income_federal_rate(self):
        """Federal rate is 37% for income over $1M."""
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("2000000"),
            state="CA",
        )
        expected_federal = Decimal("2000000") * Decimal("0.37")
        assert withholding.federal_withholding == expected_federal.quantize(Decimal("0.01"))


class TestCalculateRSUVesting:
    """Tests for the calculate_rsu_vesting function."""
    
    def test_basic_vesting(self):
        result = calculate_rsu_vesting(
            shares=Decimal("100"),
            fmv=Decimal("150"),
            vesting_date=date(2025, 3, 15),
            state="CA",
        )
        
        assert result["shares_vested"] == Decimal("100")
        assert result["fmv_per_share"] == Decimal("150")
        assert result["gross_income"] == Decimal("15000.00")
        assert result["cost_basis_per_share"] == Decimal("150")
        assert "withholding" in result
        assert result["withholding"]["total"] > 0
        assert result["net_shares"] < Decimal("100")  # Some shares for taxes
    
    def test_shares_for_taxes(self):
        """Calculates shares needed for tax withholding."""
        result = calculate_rsu_vesting(
            shares=Decimal("100"),
            fmv=Decimal("100"),  # $100/share
            vesting_date=date(2025, 3, 15),
            state="CA",
        )
        
        # Total withholding is ~40% (22% fed + 10.23% CA + 6.2% SS + 1.45% Medicare)
        # So about 40 shares needed for taxes
        assert result["shares_for_taxes"] > Decimal("35")
        assert result["shares_for_taxes"] < Decimal("45")


class TestCalculateRSUSale:
    """Tests for the calculate_rsu_sale function."""
    
    def test_basic_sale(self):
        result = calculate_rsu_sale(
            shares=Decimal("100"),
            sale_price=Decimal("200"),
            cost_basis_per_share=Decimal("150"),
            sale_date=date(2025, 6, 15),
            vesting_date=date(2025, 3, 15),
        )
        
        assert result["proceeds"] == Decimal("20000.00")
        assert result["total_cost_basis"] == Decimal("15000.00")
        assert result["capital_gain"] == Decimal("5000.00")
        assert result["is_long_term"] is False
        assert result["gain_type"] == "short_term"


class TestAnalyzeRSUScenario:
    """Tests for complete RSU scenario analysis."""
    
    def test_same_day_sale_scenario(self):
        """Same-day sale: ordinary income, no capital gain."""
        result = analyze_rsu_scenario(
            shares=Decimal("100"),
            fmv_at_vesting=Decimal("150"),
            sale_price=Decimal("150"),
            vesting_date=date(2025, 3, 15),
            sale_date=date(2025, 3, 15),
        )
        
        assert result["at_vesting"]["ordinary_income"] == Decimal("15000.00")
        assert result["at_sale"]["capital_gain"] == Decimal("0.00")
    
    def test_hold_and_profit_scenario(self):
        """Hold shares, sell higher: ordinary + capital gain."""
        result = analyze_rsu_scenario(
            shares=Decimal("100"),
            fmv_at_vesting=Decimal("150"),
            sale_price=Decimal("200"),
            vesting_date=date(2024, 1, 15),
            sale_date=date(2025, 6, 15),  # > 1 year
        )
        
        assert result["at_vesting"]["ordinary_income"] == Decimal("15000.00")
        assert result["at_sale"]["capital_gain"] == Decimal("5000.00")
        assert result["at_sale"]["is_long_term"] is True
    
    def test_hold_and_loss_scenario(self):
        """Hold shares, stock drops: ordinary income + capital loss."""
        result = analyze_rsu_scenario(
            shares=Decimal("100"),
            fmv_at_vesting=Decimal("150"),
            sale_price=Decimal("100"),
            vesting_date=date(2025, 1, 15),
            sale_date=date(2025, 6, 15),
        )
        
        assert result["at_vesting"]["ordinary_income"] == Decimal("15000.00")
        assert result["at_sale"]["capital_gain"] == Decimal("-5000.00")


class TestRSUExamples:
    """Tests for example scenario functions."""
    
    def test_same_day_sale_example(self):
        result = rsu_same_day_sale_example()
        assert result["scenario"] == "Same-Day Sale"
        assert result["at_sale"]["capital_gain"] == Decimal("0.00")
    
    def test_hold_and_sell_higher_example(self):
        result = rsu_hold_and_sell_higher_example()
        assert result["scenario"] == "Hold and Sell Higher (LTCG)"
        assert result["at_sale"]["capital_gain"] == Decimal("5000.00")
        assert result["at_sale"]["is_long_term"] is True
    
    def test_hold_and_sell_lower_example(self):
        result = rsu_hold_and_sell_lower_example()
        assert result["scenario"] == "Hold and Stock Drops (Loss)"
        assert result["at_sale"]["capital_gain"] == Decimal("-5000.00")


class TestEdgeCases:
    """Edge cases and boundary conditions."""
    
    def test_zero_shares(self):
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("0"),
            fmv_at_vesting=Decimal("150"),
        )
        assert vesting.gross_income == Decimal("0.00")
    
    def test_very_small_fmv(self):
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vesting=Decimal("0.01"),  # Penny stock
        )
        assert vesting.gross_income == Decimal("1.00")
    
    def test_large_share_count(self):
        vesting = RSUVesting(
            vesting_date=date(2025, 3, 15),
            shares_vested=Decimal("1000000"),  # 1M shares
            fmv_at_vesting=Decimal("100"),
        )
        assert vesting.gross_income == Decimal("100000000.00")  # $100M
    
    def test_withholding_zero_income(self):
        withholding = calculate_rsu_withholding(
            gross_income=Decimal("0"),
        )
        assert withholding.total_withholding == Decimal("0.00")
        assert withholding.effective_withholding_rate == Decimal("0")
