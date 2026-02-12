"""Tests for Washington state tax calculations."""

from decimal import Decimal
import pytest

from taxlens_engine.washington import (
    calculate_wa_income_tax,
    calculate_wa_capital_gains_tax,
    WaCapitalGainsExemption,
    REAL_ESTATE,
    RETIREMENT,
    SMALL_BUSINESS,
    LIVESTOCK,
    TIMBER,
    WA_CG_RATE,
    WA_CG_THRESHOLD_2025,
)


class TestWaIncomeTax:
    """Washington has no state income tax — always $0."""

    @pytest.mark.parametrize("income", [
        Decimal("0"),
        Decimal("50000"),
        Decimal("100000"),
        Decimal("250000"),
        Decimal("500000"),
        Decimal("1000000"),
        Decimal("10000000"),
    ])
    def test_always_zero(self, income):
        assert calculate_wa_income_tax(income) == Decimal("0")

    def test_default_args(self):
        assert calculate_wa_income_tax() == Decimal("0")


class TestWaCapitalGainsTax:
    """WA capital gains: 7% on LTCG exceeding $270,000."""

    def test_zero_gains(self):
        assert calculate_wa_capital_gains_tax(Decimal("0")) == Decimal("0")

    def test_negative_gains(self):
        assert calculate_wa_capital_gains_tax(Decimal("-50000")) == Decimal("0")

    def test_below_threshold(self):
        assert calculate_wa_capital_gains_tax(Decimal("200000")) == Decimal("0")

    def test_at_threshold_exactly(self):
        assert calculate_wa_capital_gains_tax(Decimal("270000")) == Decimal("0")

    def test_one_dollar_over_threshold(self):
        result = calculate_wa_capital_gains_tax(Decimal("270001"))
        assert result == Decimal("0.07")

    def test_500k_gains(self):
        # 7% of (500000 - 270000) = 7% of 230000 = 16100
        result = calculate_wa_capital_gains_tax(Decimal("500000"))
        assert result == Decimal("16100.00")

    def test_1m_gains(self):
        # 7% of (1000000 - 270000) = 7% of 730000 = 51100
        result = calculate_wa_capital_gains_tax(Decimal("1000000"))
        assert result == Decimal("51100.00")

    def test_just_below_threshold(self):
        assert calculate_wa_capital_gains_tax(Decimal("269999.99")) == Decimal("0")


class TestWaCapitalGainsExemptions:
    """Exemption scenarios."""

    def test_real_estate_fully_exempt(self):
        # $400K gains, all from real estate → $0 tax
        exemptions = [(REAL_ESTATE, Decimal("400000"))]
        result = calculate_wa_capital_gains_tax(Decimal("400000"), exemptions=exemptions)
        assert result == Decimal("0")

    def test_retirement_fully_exempt(self):
        exemptions = [(RETIREMENT, Decimal("500000"))]
        result = calculate_wa_capital_gains_tax(Decimal("500000"), exemptions=exemptions)
        assert result == Decimal("0")

    def test_partial_exemption(self):
        # $500K total, $100K exempt → $400K taxable, 7% of ($400K - $270K) = 7% of $130K = $9100
        exemptions = [(REAL_ESTATE, Decimal("100000"))]
        result = calculate_wa_capital_gains_tax(Decimal("500000"), exemptions=exemptions)
        assert result == Decimal("9100.00")

    def test_exemption_brings_below_threshold(self):
        # $300K total, $100K exempt → $200K taxable → below threshold
        exemptions = [(SMALL_BUSINESS, Decimal("100000"))]
        result = calculate_wa_capital_gains_tax(Decimal("300000"), exemptions=exemptions)
        assert result == Decimal("0")

    def test_multiple_exemptions(self):
        # $600K total, $150K real estate + $100K retirement = $250K exempt
        # Taxable: $350K, excess: $350K - $270K = $80K, tax: $5600
        exemptions = [
            (REAL_ESTATE, Decimal("150000")),
            (RETIREMENT, Decimal("100000")),
        ]
        result = calculate_wa_capital_gains_tax(Decimal("600000"), exemptions=exemptions)
        assert result == Decimal("5600.00")

    def test_livestock_exemption(self):
        exemptions = [(LIVESTOCK, Decimal("300000"))]
        result = calculate_wa_capital_gains_tax(Decimal("300000"), exemptions=exemptions)
        assert result == Decimal("0")

    def test_timber_exemption(self):
        exemptions = [(TIMBER, Decimal("50000"))]
        # $400K - $50K = $350K taxable, excess $80K, tax $5600
        result = calculate_wa_capital_gains_tax(Decimal("400000"), exemptions=exemptions)
        assert result == Decimal("5600.00")

    def test_exemption_exceeds_gains(self):
        # Exempt more than gains → $0
        exemptions = [(REAL_ESTATE, Decimal("500000"))]
        result = calculate_wa_capital_gains_tax(Decimal("300000"), exemptions=exemptions)
        assert result == Decimal("0")

    def test_no_exemptions_none(self):
        result = calculate_wa_capital_gains_tax(Decimal("500000"), exemptions=None)
        assert result == Decimal("16100.00")

    def test_empty_exemptions_list(self):
        result = calculate_wa_capital_gains_tax(Decimal("500000"), exemptions=[])
        assert result == Decimal("16100.00")


class TestWaConstants:
    """Verify constants."""

    def test_rate(self):
        assert WA_CG_RATE == Decimal("0.07")

    def test_threshold(self):
        assert WA_CG_THRESHOLD_2025 == Decimal("270000")

    def test_exemption_enum_values(self):
        assert WaCapitalGainsExemption.REAL_ESTATE.value == "real_estate"
        assert WaCapitalGainsExemption.RETIREMENT.value == "retirement"
        assert WaCapitalGainsExemption.SMALL_BUSINESS.value == "small_business"
        assert WaCapitalGainsExemption.LIVESTOCK.value == "livestock"
        assert WaCapitalGainsExemption.TIMBER.value == "timber"
