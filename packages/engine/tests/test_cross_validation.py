"""
Cross-validation test suite for TaxLens Engine.

Validates TaxLens federal tax calculations against hand-computed IRS reference
values using 2025 tax rules. 20 scenarios covering simple W-2, equity compensation,
high-income, FICA/payroll, and deduction cases.

Reference: IRS Rev. Proc. 2024-40 (2025 inflation adjustments)
Note: PSLmodels/Tax-Calculator (taxcalc 6.4) was installed but calc_all() hangs
on single-record DataFrames, so hand-computed IRS values are used as reference.
"""

import pytest
from decimal import Decimal

from taxlens_engine.models import FilingStatus, IncomeBreakdown
from taxlens_engine.calculator import calculate_taxes

D = Decimal

# Tolerance for comparison (cents)
TOLERANCE = D("0.01")


def assert_close(actual, expected, label="", tolerance=TOLERANCE):
    """Assert two Decimal values are within tolerance."""
    diff = abs(actual - expected)
    assert diff <= tolerance, (
        f"{label}: expected {expected}, got {actual}, diff={diff}"
    )


# ============================================================
# Hand-computed reference values for 2025 tax year
# Using IRS 2025 brackets, standard deductions, FICA rates
# ============================================================

SCENARIOS = [
    # --- Simple W-2 scenarios ---
    {
        "name": "S01: Single, $75K wages",
        "income": dict(w2_wages=D("75000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "deduction_used": D("15000"),
            "federal_tax_on_ordinary": D("8114.00"),
            "federal_tax_on_ltcg": D("0"),
            "amt_owed": D("0"),
            "social_security_tax": D("4650.00"),
            "medicare_tax": D("1087.50"),
            "additional_medicare_tax": D("0"),
            "niit": D("0"),
            "total_tax": D("13851.50"),
        },
    },
    {
        "name": "S02: Single, $150K wages",
        "income": dict(w2_wages=D("150000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "deduction_used": D("15000"),
            "federal_tax_on_ordinary": D("25247.00"),
            "social_security_tax": D("9300.00"),
            "medicare_tax": D("2175.00"),
            "additional_medicare_tax": D("0"),
            "niit": D("0"),
            "total_tax": D("36722.00"),
        },
    },
    {
        "name": "S03: MFJ, $150K wages",
        "income": dict(w2_wages=D("150000")),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "deduction_used": D("30000"),
            "federal_tax_on_ordinary": D("16228.00"),
            "social_security_tax": D("9300.00"),
            "medicare_tax": D("2175.00"),
            "additional_medicare_tax": D("0"),
            "total_tax": D("27703.00"),
        },
    },
    {
        "name": "S04: MFJ, $300K wages",
        "income": dict(w2_wages=D("300000")),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "deduction_used": D("30000"),
            "federal_tax_on_ordinary": D("50494.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("4350.00"),
            "additional_medicare_tax": D("450.00"),
            "niit": D("0"),
            "total_tax": D("66212.20"),
        },
    },
    {
        "name": "S05: HoH, $50K wages",
        "income": dict(w2_wages=D("50000")),
        "filing_status": FilingStatus.HEAD_OF_HOUSEHOLD,
        "itemized_deductions": D("0"),
        "expected": {
            "deduction_used": D("22500"),
            "federal_tax_on_ordinary": D("2960.00"),
            "social_security_tax": D("3100.00"),
            "medicare_tax": D("725.00"),
            "total_tax": D("6785.00"),
        },
    },
    # --- Equity scenarios ---
    {
        "name": "S06: Single, $200K W2 + $100K RSU",
        "income": dict(w2_wages=D("200000"), rsu_income=D("100000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("69297.25"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("4350.00"),
            "additional_medicare_tax": D("900.00"),
            "niit": D("0"),
            "total_tax": D("85465.45"),
        },
    },
    {
        "name": "S07: MFJ, $300K W2 + $200K RSU + $50K LTCG",
        "income": dict(
            w2_wages=D("300000"), rsu_income=D("200000"),
            long_term_gains=D("50000"),
        ),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("104526.00"),
            "federal_tax_on_ltcg": D("7500.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("7250.00"),
            "additional_medicare_tax": D("2250.00"),
            "niit": D("1900.00"),
            "total_tax": D("134344.20"),
        },
    },
    {
        "name": "S08: Single, $250K W2 + ISO exercise ($100K bargain) - AMT",
        "income": dict(w2_wages=D("250000"), iso_bargain_element=D("100000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("52263.00"),
            # AMT threshold corrected to $239,100 (Rev. Proc. 2024-40); was $232,600
            # AMTI=$335K; exempt=$88.1K; taxable=$246.9K
            # TMT = 26%×$239,100 + 28%×$7,800 = $62,166+$2,184 = $64,350
            # AMT owed = $64,350 - $52,263 = $12,087
            "amt_owed": D("12087.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("3625.00"),
            "additional_medicare_tax": D("450.00"),
            "niit": D("0"),
            "total_tax": D("79343.20"),
        },
    },
    {
        "name": "S09: Single, $400K W2 + $30K ESPP disqualifying disposition",
        "income": dict(w2_wages=D("400000"), short_term_gains=D("30000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("114797.25"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("5800.00"),  # only on W2 wages
            "additional_medicare_tax": D("1800.00"),
            "niit": D("1140.00"),
            "total_tax": D("134455.45"),
        },
    },
    {
        "name": "S10: MFJ, $500K W2 + $150K RSU + $80K LTCG + $20K STCG",
        "income": dict(
            w2_wages=D("500000"), rsu_income=D("150000"),
            long_term_gains=D("80000"), short_term_gains=D("20000"),
        ),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("163094.50"),
            "federal_tax_on_ltcg": D("16000.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("9425.00"),
            "additional_medicare_tax": D("3600.00"),
            "niit": D("3800.00"),
            "total_tax": D("206837.70"),
        },
    },
    # --- High-income scenarios ---
    {
        "name": "S11: Single, $800K wages (35% bracket)",
        "income": dict(w2_wages=D("800000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("247470.25"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("11600.00"),
            "additional_medicare_tax": D("5400.00"),
            "total_tax": D("275388.45"),
        },
    },
    {
        "name": "S12: MFJ, $1M wages (37% bracket + addl Medicare)",
        "income": dict(w2_wages=D("1000000")),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("282962.50"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("14500.00"),
            "additional_medicare_tax": D("6750.00"),
            "total_tax": D("315130.70"),
        },
    },
    {
        "name": "S13: Single, $600K W2 + $200K LTCG (NIIT 3.8%)",
        "income": dict(w2_wages=D("600000"), long_term_gains=D("200000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("174297.25"),
            "federal_tax_on_ltcg": D("40000.00"),
            "niit": D("7600.00"),
            "total_tax": D("245115.45"),
        },
    },
    {
        "name": "S14: MFJ, $400K W2 + $100K qualified dividends",
        "income": dict(w2_wages=D("400000"), qualified_dividends=D("100000")),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("74494.00"),
            "federal_tax_on_ltcg": D("15000.00"),
            "niit": D("3800.00"),
            "total_tax": D("111362.20"),
        },
    },
    {
        "name": "S15: Single, $300K W2 + $200K ISO bargain (heavy AMT)",
        "income": dict(w2_wages=D("300000"), iso_bargain_element=D("200000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("69297.25"),
            # AMT threshold corrected to $239,100 (Rev. Proc. 2024-40); was $232,600
            # AMTI=$485K; exempt=$88.1K; taxable=$396.9K
            # TMT = 26%×$239,100 + 28%×$157,800 = $62,166+$44,184 = $106,350
            # AMT owed = $106,350 - $69,297.25 = $37,052.75
            "amt_owed": D("37052.75"),
            "total_tax": D("122518.20"),
        },
    },
    # --- FICA/payroll scenarios ---
    {
        "name": "S16: Single, $160K (near SS wage base $176,100)",
        "income": dict(w2_wages=D("160000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("27647.00"),
            "social_security_tax": D("9920.00"),
            "medicare_tax": D("2320.00"),
            "additional_medicare_tax": D("0"),
            "total_tax": D("39887.00"),
        },
    },
    {
        "name": "S17: Single, $250K (addl Medicare at $200K single)",
        "income": dict(w2_wages=D("250000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("52263.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("3625.00"),
            "additional_medicare_tax": D("450.00"),
            "total_tax": D("67256.20"),
        },
    },
    {
        "name": "S18: MFJ, $350K (addl Medicare at $250K MFJ)",
        "income": dict(w2_wages=D("350000")),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        "itemized_deductions": D("0"),
        "expected": {
            "federal_tax_on_ordinary": D("62494.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("5075.00"),
            "additional_medicare_tax": D("900.00"),
            "total_tax": D("79387.20"),
        },
    },
    # --- Deduction scenarios ---
    {
        "name": "S19: MFJ, $200K, itemized ($10K SALT-capped + $20K mortgage + $10K charity = $40K)",
        "income": dict(w2_wages=D("200000")),
        "filing_status": FilingStatus.MARRIED_JOINTLY,
        # SALT capped at $10K (2025), not $35K. Mortgage + charity pass through.
        # Actual allowed itemized = $10K + $20K + $10K = $40K > $30K standard
        "itemized_deductions": D("40000"),
        "expected": {
            "deduction_used": D("40000"),
            "federal_tax_on_ordinary": D("25028.00"),
            "social_security_tax": D("10918.20"),
            "medicare_tax": D("2900.00"),
            "total_tax": D("38846.20"),
        },
    },
    {
        "name": "S20: Single, $100K, standard deduction",
        "income": dict(w2_wages=D("100000")),
        "filing_status": FilingStatus.SINGLE,
        "itemized_deductions": D("0"),
        "expected": {
            "deduction_used": D("15000"),
            "federal_tax_on_ordinary": D("13614.00"),
            "social_security_tax": D("6200.00"),
            "medicare_tax": D("1450.00"),
            "total_tax": D("21264.00"),
        },
    },
]


class TestCrossValidation:
    """Cross-validation of TaxLens engine against IRS reference calculations."""

    @pytest.mark.parametrize(
        "scenario",
        SCENARIOS,
        ids=[s["name"] for s in SCENARIOS],
    )
    def test_scenario(self, scenario):
        """Validate TaxLens output against hand-computed IRS reference values."""
        income = IncomeBreakdown(**scenario["income"])
        result = calculate_taxes(
            income=income,
            filing_status=scenario["filing_status"],
            itemized_deductions=scenario.get("itemized_deductions", D("0")),
        )

        expected = scenario["expected"]
        for field, expected_val in expected.items():
            actual_val = getattr(result, field)
            assert_close(
                actual_val,
                expected_val,
                label=f"{scenario['name']} → {field}",
            )

    def test_s19_salt_cap_documentation(self):
        """
        Document that TaxLens does NOT enforce the $10K SALT cap internally.
        The caller must apply the SALT cap before passing itemized_deductions.
        This is by design — the engine takes pre-computed deduction totals.
        """
        income = IncomeBreakdown(w2_wages=D("200000"))
        
        # If caller passes raw $65K ($35K SALT + $20K mortgage + $10K charity)
        # without applying SALT cap, engine will use $65K
        result_uncapped = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            itemized_deductions=D("65000"),
        )
        
        # With SALT cap applied: $10K + $20K + $10K = $40K
        result_capped = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            itemized_deductions=D("40000"),
        )
        
        # The capped version should have higher tax (lower deduction)
        assert result_capped.total_tax > result_uncapped.total_tax
        assert result_capped.deduction_used == D("40000")
        assert result_uncapped.deduction_used == D("65000")

    def test_s20_standard_vs_itemized(self):
        """Verify standard deduction is used when itemized is lower."""
        income = IncomeBreakdown(w2_wages=D("100000"))
        
        # With low itemized ($10K < $15K standard)
        result_low = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            itemized_deductions=D("10000"),
        )
        
        # Standard deduction should win
        assert result_low.deduction_used == D("15000")
        
        # With high itemized ($20K > $15K standard)
        result_high = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            itemized_deductions=D("20000"),
        )
        
        # Itemized should win
        assert result_high.deduction_used == D("20000")
        assert result_high.total_tax < result_low.total_tax

    def test_fica_wages_include_rsu(self):
        """Verify RSU income is included in FICA wage base."""
        income = IncomeBreakdown(w2_wages=D("100000"), rsu_income=D("100000"))
        result = calculate_taxes(income, FilingStatus.SINGLE)
        
        # FICA on $200K: SS capped at $176,100
        assert_close(result.social_security_tax, D("10918.20"), "SS tax")
        assert_close(result.medicare_tax, D("2900.00"), "Medicare")

    def test_niit_threshold_single_vs_mfj(self):
        """Verify different NIIT thresholds for Single vs MFJ."""
        income = IncomeBreakdown(
            w2_wages=D("200000"), long_term_gains=D("50000")
        )
        
        # Single: MAGI $250K > $200K threshold → NIIT applies
        result_single = calculate_taxes(income, FilingStatus.SINGLE)
        assert result_single.niit > D("0")
        assert_close(result_single.niit, D("1900.00"), "Single NIIT")
        
        # MFJ: MAGI $250K = $250K threshold → NIIT = 0
        result_mfj = calculate_taxes(income, FilingStatus.MARRIED_JOINTLY)
        assert result_mfj.niit == D("0")
