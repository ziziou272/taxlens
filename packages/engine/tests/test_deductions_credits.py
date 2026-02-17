"""
Tests for the 5 new tax features:
1. Itemized Deductions
2. Above-the-Line Deductions
3. Child Tax Credit / ACTC / Other Dependent Credit
4. Earned Income Credit (EITC)
5. Education Credits (AOTC / LLC)
"""

from decimal import Decimal
import pytest

from taxlens_engine.models import FilingStatus, TaxYear
from taxlens_engine.federal import (
    calculate_itemized_deductions,
    calculate_above_the_line_deductions,
    calculate_child_tax_credit,
    calculate_eitc,
    calculate_education_credits,
)
from taxlens_engine.calculator import calculate_taxes
from taxlens_engine.models import IncomeBreakdown


# ===========================================================================
# 1. Itemized Deductions
# ===========================================================================

class TestItemizedDeductions:

    def test_salt_cap_general(self):
        """SALT capped at $10,000 for single filer."""
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            salt_paid=Decimal("15000"),
        )
        assert detail.salt == Decimal("10000")
        assert detail.salt_paid == Decimal("15000")

    def test_salt_cap_mfs(self):
        """SALT capped at $5,000 for MFS."""
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.MARRIED_SEPARATELY,
            salt_paid=Decimal("15000"),
        )
        assert detail.salt == Decimal("5000")

    def test_salt_under_cap(self):
        """SALT under cap passes through unchanged."""
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            salt_paid=Decimal("7000"),
        )
        assert detail.salt == Decimal("7000")

    def test_medical_floor_75_pct(self):
        """Medical: only amount exceeding 7.5% of AGI is deductible."""
        # AGI $100K → floor $7,500; paid $12,000 → deductible $4,500
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            medical_expenses=Decimal("12000"),
        )
        assert detail.medical == Decimal("4500")
        assert detail.medical_paid == Decimal("12000")

    def test_medical_below_floor(self):
        """Medical expenses below 7.5% floor = $0 deductible."""
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            medical_expenses=Decimal("5000"),
        )
        assert detail.medical == Decimal("0")

    def test_mortgage_under_750k_loan(self):
        """Full mortgage interest when loan ≤ $750K."""
        detail = calculate_itemized_deductions(
            agi=Decimal("200000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
            mortgage_interest=Decimal("30000"),
            mortgage_loan_balance=Decimal("600000"),
        )
        assert detail.mortgage_interest == Decimal("30000")

    def test_mortgage_over_750k_loan_prorated(self):
        """Mortgage interest prorated when loan > $750K."""
        # Loan $1,000,000; interest $40,000 → deductible = $40,000 × (750/1000) = $30,000
        detail = calculate_itemized_deductions(
            agi=Decimal("300000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
            mortgage_interest=Decimal("40000"),
            mortgage_loan_balance=Decimal("1000000"),
        )
        assert detail.mortgage_interest == Decimal("30000")

    def test_charitable_passes_through(self):
        """Charitable contributions pass through as-is."""
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            charitable=Decimal("5000"),
        )
        assert detail.charitable == Decimal("5000")

    def test_total_is_sum_of_components(self):
        """Total equals sum of all component deductions."""
        detail = calculate_itemized_deductions(
            agi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            mortgage_interest=Decimal("15000"),
            salt_paid=Decimal("12000"),  # capped at $10K
            charitable=Decimal("3000"),
            medical_expenses=Decimal("12000"),  # $4,500 deductible
        )
        expected = Decimal("15000") + Decimal("10000") + Decimal("3000") + Decimal("4500")
        assert detail.total == expected

    def test_standard_beats_itemized(self):
        """Calculator auto-selects standard when it's higher."""
        income = IncomeBreakdown(w2_wages=Decimal("100000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            salt_paid=Decimal("3000"),  # Itemized would be $3K < $15K standard
        )
        assert result.deduction_used == result.standard_deduction

    def test_itemized_beats_standard(self):
        """Calculator auto-selects itemized when higher."""
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            mortgage_interest=Decimal("20000"),
            salt_paid=Decimal("12000"),  # capped at $10K
            charitable=Decimal("5000"),
        )
        # Itemized = $35K > MFJ standard $30K
        assert result.deduction_used == result.itemized_deductions_detail.total
        assert result.deduction_used > result.standard_deduction


# ===========================================================================
# 2. Above-the-Line Deductions
# ===========================================================================

class TestAboveTheLineDeductions:

    def test_401k_capped_at_limit(self):
        """401(k) contribution capped at $23,500."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("200000"),
            filing_status=FilingStatus.SINGLE,
            contributions_401k=Decimal("30000"),  # Over limit
        )
        assert detail.contributions_401k == Decimal("23500")

    def test_401k_catchup_over_50(self):
        """401(k) catch-up limit ($7,500) applies for age 50+."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("200000"),
            filing_status=FilingStatus.SINGLE,
            contributions_401k=Decimal("31000"),
            age_over_50=True,
        )
        assert detail.contributions_401k == Decimal("31000")  # $23,500 + $7,500

    def test_ira_capped(self):
        """IRA capped at $7,000."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            ira_contributions=Decimal("10000"),
        )
        assert detail.ira_contributions == Decimal("7000")

    def test_ira_catchup(self):
        """IRA catch-up $1,000 for age 50+."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            ira_contributions=Decimal("8000"),
            age_over_50=True,
        )
        assert detail.ira_contributions == Decimal("8000")

    def test_hsa_single_limit(self):
        """HSA limited to $4,300 for single coverage."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            hsa_contributions=Decimal("6000"),
        )
        assert detail.hsa_contributions == Decimal("4300")

    def test_hsa_family_limit(self):
        """HSA family limit $8,550 for MFJ."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("200000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
            hsa_contributions=Decimal("10000"),
        )
        assert detail.hsa_contributions == Decimal("8550")

    def test_student_loan_capped_at_2500(self):
        """Student loan interest capped at $2,500."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("60000"),
            filing_status=FilingStatus.SINGLE,
            student_loan_interest=Decimal("4000"),
        )
        assert detail.student_loan_interest == Decimal("2500")

    def test_student_loan_phase_out_single(self):
        """Student loan interest phases out $80K–$95K for single."""
        # At $87,500 (midpoint): 50% phase-out → $1,250 deductible
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("87500"),
            filing_status=FilingStatus.SINGLE,
            student_loan_interest=Decimal("2500"),
        )
        assert detail.student_loan_interest == Decimal("1250.00")

    def test_student_loan_fully_phased_out(self):
        """Student loan interest $0 at/above $95K (single)."""
        detail = calculate_above_the_line_deductions(
            gross_income=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            student_loan_interest=Decimal("2500"),
        )
        assert detail.student_loan_interest == Decimal("0")

    def test_agi_reduced_by_401k(self):
        """Calculator correctly reduces AGI by 401(k) contribution."""
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            contributions_401k=Decimal("23500"),
        )
        # AGI should be $200K - $23,500 = $176,500
        assert result.agi == Decimal("176500.00")
        assert result.above_the_line_deductions.contributions_401k == Decimal("23500")


# ===========================================================================
# 3. Child Tax Credit / ACTC / Other Dependent Credit
# ===========================================================================

class TestChildTaxCredit:

    def test_ctc_two_children_below_phaseout(self):
        """2 children, income below phase-out: full $4,000 CTC."""
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("150000"),
            filing_status=FilingStatus.SINGLE,
            num_children_under_17=2,
            federal_tax_before_credits=Decimal("20000"),
        )
        assert ctc == Decimal("4000")

    def test_ctc_phases_out_single(self):
        """CTC phases out above $200K for single."""
        # $210K income → $10K over threshold → $500 reduction per $1K × 10 = $500
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("210000"),
            filing_status=FilingStatus.SINGLE,
            num_children_under_17=2,
            federal_tax_before_credits=Decimal("40000"),
        )
        # 2 × $2,000 = $4,000; $10K over threshold → ceiling($10K/$1K) = 10 increments × $50 = $500 reduction
        assert ctc == Decimal("3500")

    def test_ctc_phases_out_mfj(self):
        """CTC phases out above $400K for MFJ."""
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("401000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
            num_children_under_17=1,
            federal_tax_before_credits=Decimal("80000"),
        )
        # $1K over → 1 increment × $50 = $50 reduction; $2,000 - $50 = $1,950
        assert ctc == Decimal("1950")

    def test_ctc_fully_phased_out(self):
        """CTC goes to zero at high income."""
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("500000"),
            filing_status=FilingStatus.SINGLE,
            num_children_under_17=1,
            federal_tax_before_credits=Decimal("100000"),
        )
        assert ctc == Decimal("0")

    def test_other_dependent_credit(self):
        """$500 per other dependent."""
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("100000"),
            filing_status=FilingStatus.SINGLE,
            num_children_under_17=0,
            num_other_dependents=2,
            federal_tax_before_credits=Decimal("5000"),
        )
        assert odc == Decimal("1000")

    def test_actc_refundable(self):
        """ACTC applies when CTC exceeds tax liability."""
        # Tax = $500, CTC = $2,000 → non-refundable $500, unused $1,500 → ACTC up to $1,700
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            num_children_under_17=1,
            federal_tax_before_credits=Decimal("500"),
        )
        assert ctc == Decimal("500")      # limited to tax
        assert actc == Decimal("1500")    # remaining $1,500 (under $1,700 cap)

    def test_actc_capped_at_1700_per_child(self):
        """ACTC capped at $1,700 per qualifying child."""
        ctc, odc, actc = calculate_child_tax_credit(
            magi=Decimal("30000"),
            filing_status=FilingStatus.SINGLE,
            num_children_under_17=2,
            federal_tax_before_credits=Decimal("0"),  # No tax to offset
        )
        # ACTC limited to $1,700 × 2 = $3,400
        assert actc == Decimal("3400")

    def test_ctc_in_full_calculator(self):
        """Child tax credit flows through full calculator."""
        income = IncomeBreakdown(w2_wages=Decimal("60000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            num_children_under_17=2,
        )
        assert result.child_tax_credit > Decimal("0") or result.actc > Decimal("0")
        assert result.total_credits > Decimal("0")


# ===========================================================================
# 4. Earned Income Credit (EITC)
# ===========================================================================

class TestEITC:

    def test_eitc_no_children_max(self):
        """No children: max EITC $632 at optimal income."""
        eitc = calculate_eitc(
            earned_income=Decimal("10000"),
            agi=Decimal("10000"),
            filing_status=FilingStatus.SINGLE,
            num_children=0,
        )
        assert eitc == Decimal("632")  # Should be at/near max

    def test_eitc_one_child_max(self):
        """1 child: max EITC $4,213 at phase-in income."""
        eitc = calculate_eitc(
            earned_income=Decimal("15000"),
            agi=Decimal("15000"),
            filing_status=FilingStatus.SINGLE,
            num_children=1,
        )
        assert eitc == Decimal("4213")

    def test_eitc_two_children_max(self):
        """2 children: max EITC $6,960."""
        eitc = calculate_eitc(
            earned_income=Decimal("20000"),
            agi=Decimal("20000"),
            filing_status=FilingStatus.SINGLE,
            num_children=2,
        )
        assert eitc == Decimal("6960")

    def test_eitc_three_plus_children_max(self):
        """3+ children: max EITC $7,830."""
        eitc = calculate_eitc(
            earned_income=Decimal("20000"),
            agi=Decimal("20000"),
            filing_status=FilingStatus.SINGLE,
            num_children=3,
        )
        assert eitc == Decimal("7830")

    def test_eitc_phases_out(self):
        """EITC phases out at higher income."""
        # Single, no children: phase-out starts $10,330, ends ~$18,591
        eitc_low = calculate_eitc(
            earned_income=Decimal("10000"),
            agi=Decimal("10000"),
            filing_status=FilingStatus.SINGLE,
            num_children=0,
        )
        eitc_high = calculate_eitc(
            earned_income=Decimal("15000"),
            agi=Decimal("15000"),
            filing_status=FilingStatus.SINGLE,
            num_children=0,
        )
        assert eitc_high < eitc_low

    def test_eitc_zero_above_phaseout(self):
        """EITC is $0 above phase-out threshold."""
        eitc = calculate_eitc(
            earned_income=Decimal("20000"),
            agi=Decimal("20000"),
            filing_status=FilingStatus.SINGLE,
            num_children=0,
        )
        assert eitc == Decimal("0")

    def test_eitc_mfj_higher_phaseout(self):
        """MFJ gets higher income threshold before phase-out."""
        eitc_mfj = calculate_eitc(
            earned_income=Decimal("15000"),
            agi=Decimal("15000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
            num_children=0,
        )
        eitc_single = calculate_eitc(
            earned_income=Decimal("15000"),
            agi=Decimal("15000"),
            filing_status=FilingStatus.SINGLE,
            num_children=0,
        )
        # At $15K: single is phasing out, MFJ not yet; MFJ should be higher
        assert eitc_mfj >= eitc_single

    def test_eitc_investment_income_disqualifies(self):
        """Investment income over $11,600 disqualifies EITC."""
        eitc = calculate_eitc(
            earned_income=Decimal("20000"),
            agi=Decimal("30000"),
            filing_status=FilingStatus.SINGLE,
            num_children=1,
            investment_income=Decimal("12000"),
        )
        assert eitc == Decimal("0")

    def test_eitc_mfs_ineligible(self):
        """Married Filing Separately is ineligible for EITC."""
        eitc = calculate_eitc(
            earned_income=Decimal("20000"),
            agi=Decimal("20000"),
            filing_status=FilingStatus.MARRIED_SEPARATELY,
            num_children=1,
        )
        assert eitc == Decimal("0")

    def test_eitc_no_earned_income(self):
        """No earned income → no EITC."""
        eitc = calculate_eitc(
            earned_income=Decimal("0"),
            agi=Decimal("5000"),
            filing_status=FilingStatus.SINGLE,
            num_children=0,
        )
        assert eitc == Decimal("0")


# ===========================================================================
# 5. Education Credits (AOTC / LLC)
# ===========================================================================

class TestEducationCredits:

    def test_aotc_max_credit(self):
        """AOTC max $2,500 (100% of first $2K + 25% of next $2K)."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("4000"),
            education_type="aotc",
        )
        # $2,000×100% + $2,000×25% = $2,500; 40% refundable = $1,000
        assert non_ref + refundable == Decimal("2500")
        assert refundable == Decimal("1000")
        assert non_ref == Decimal("1500")

    def test_aotc_partial_expenses(self):
        """AOTC proportional for expenses < $4K."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("2000"),
            education_type="aotc",
        )
        # $2,000 × 100% = $2,000; 40% refundable = $800
        total = non_ref + refundable
        assert total == Decimal("2000")
        assert refundable == Decimal("800.00")

    def test_aotc_phases_out_single(self):
        """AOTC phases out $80K–$90K for single."""
        # At $85K (midpoint): 50% phase-out
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("85000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("4000"),
            education_type="aotc",
        )
        # Half of $2,500 = $1,250
        assert non_ref + refundable == Decimal("1250.00")

    def test_aotc_fully_phased_out(self):
        """AOTC $0 above $90K for single."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("95000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("4000"),
            education_type="aotc",
        )
        assert non_ref == Decimal("0")
        assert refundable == Decimal("0")

    def test_aotc_mfj_higher_phaseout(self):
        """AOTC phases out $160K–$180K for MFJ."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("170000"),
            filing_status=FilingStatus.MARRIED_JOINTLY,
            education_expenses=Decimal("4000"),
            education_type="aotc",
        )
        # 50% phase-out at midpoint
        assert non_ref + refundable == Decimal("1250.00")

    def test_llc_max_2000(self):
        """LLC max $2,000 (20% of first $10K expenses)."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("10000"),
            education_type="llc",
        )
        assert non_ref == Decimal("2000")
        assert refundable == Decimal("0")  # LLC is non-refundable

    def test_llc_partial(self):
        """LLC proportional for expenses < $10K."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("50000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("5000"),
            education_type="llc",
        )
        assert non_ref == Decimal("1000.00")

    def test_llc_phases_out(self):
        """LLC phases out $80K–$90K single (same as AOTC range)."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("85000"),
            filing_status=FilingStatus.SINGLE,
            education_expenses=Decimal("10000"),
            education_type="llc",
        )
        assert non_ref == Decimal("1000.00")  # 50% of $2,000

    def test_education_mfs_ineligible(self):
        """MFS is ineligible for education credits."""
        non_ref, refundable = calculate_education_credits(
            magi=Decimal("50000"),
            filing_status=FilingStatus.MARRIED_SEPARATELY,
            education_expenses=Decimal("4000"),
            education_type="aotc",
        )
        assert non_ref == Decimal("0")
        assert refundable == Decimal("0")


# ===========================================================================
# Integration: Full sample scenario
# $200K wages, MFJ, 2 kids, $20K mortgage interest, $12K SALT, $5K charity,
# $23,500 401k
# ===========================================================================

class TestSampleScenario:

    def test_sample_scenario(self):
        """
        $200K wages, MFJ, 2 kids, $20K mortgage interest, $12K SALT,
        $5K charity, $23,500 401k.

        Expected approximate values:
          - AGI: $200K - $23,500 = $176,500
          - Itemized: $20K + $10K(SALT cap) + $5K = $35K (beats $30K standard)
          - Taxable income ≈ $176,500 - $35,000 = $141,500
          - Federal tax ~$18-22K (before credits)
          - CTC: $4,000 (2 × $2,000, below MFJ phase-out threshold)
        """
        income = IncomeBreakdown(w2_wages=Decimal("200000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.MARRIED_JOINTLY,
            contributions_401k=Decimal("23500"),
            mortgage_interest=Decimal("20000"),
            salt_paid=Decimal("12000"),
            charitable=Decimal("5000"),
            num_children_under_17=2,
        )

        # AGI check
        assert result.agi == Decimal("176500.00")

        # Above-the-line deductions
        assert result.above_the_line_deductions.contributions_401k == Decimal("23500")

        # SALT capped at $10K
        assert result.itemized_deductions_detail.salt == Decimal("10000")
        assert result.itemized_deductions_detail.mortgage_interest == Decimal("20000")
        assert result.itemized_deductions_detail.charitable == Decimal("5000")

        # Itemized $35K > standard $30K → itemized wins
        assert result.deduction_used == Decimal("35000")

        # Taxable income = $176,500 - $35,000 = $141,500
        assert result.taxable_income == Decimal("141500")

        # Child Tax Credit: 2 × $2,000 = $4,000 (income well below $400K MFJ threshold)
        assert result.child_tax_credit == Decimal("4000")

        # Federal tax before credits should be non-trivial
        gross_federal = (
            result.federal_tax_on_ordinary
            + result.federal_tax_on_ltcg
            + result.amt_owed
        )
        assert gross_federal > Decimal("0")

        # Total credits at least $4,000
        assert result.total_credits >= Decimal("4000")

        # Effective rate should be reasonable (5-20% range given credits)
        assert Decimal("0.03") < result.effective_rate < Decimal("0.25")

    def test_backward_compat_no_new_fields(self):
        """Existing callers with no new fields work exactly as before."""
        income = IncomeBreakdown(w2_wages=Decimal("150000"))
        result = calculate_taxes(
            income=income,
            filing_status=FilingStatus.SINGLE,
            state="CA",
        )
        # Basic sanity checks
        assert result.federal_tax_total > 0
        assert result.state_tax > 0
        assert result.total_credits == Decimal("0")
        assert result.above_the_line_deductions.total == Decimal("0")
        assert result.agi == result.income.total_income
