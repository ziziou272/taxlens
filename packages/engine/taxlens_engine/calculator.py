"""
Complete tax calculator for TaxLens.

Integrates federal, state, and payroll taxes into a comprehensive summary.

AGI Calculation Order
---------------------
1. Gross income
2. Above-the-line deductions  → AGI
3. max(standard, itemized)    → Taxable income
4. Federal income tax
5. Apply credits (non-refundable first, then refundable)
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from pydantic import BaseModel

from taxlens_engine.models import (
    FilingStatus,
    IncomeBreakdown,
    TaxSummary,
    TaxYear,
    ItemizedDeductionsDetail,
    AboveTheLineDeductionsDetail,
)
from taxlens_engine.federal import (
    calculate_federal_tax,
    calculate_ltcg_tax,
    calculate_amt,
    calculate_fica,
    calculate_niit,
    get_marginal_rate,
    calculate_itemized_deductions,
    calculate_above_the_line_deductions,
    calculate_child_tax_credit,
    calculate_eitc,
    calculate_education_credits,
)
from taxlens_engine.california import (
    calculate_california_tax,
    get_ca_standard_deduction,
    get_ca_marginal_rate,
    calculate_sdi,
)
from taxlens_engine.new_york import (
    calculate_ny_tax,
    get_ny_standard_deduction,
    get_ny_marginal_rate,
)


class TaxCalculatorInput(BaseModel):
    """Input parameters for tax calculation."""
    income: IncomeBreakdown
    filing_status: FilingStatus
    state: Optional[str] = None
    year: int = 2025

    # Legacy single-value itemized deductions (still supported)
    itemized_deductions: Decimal = Decimal("0")

    # Itemized deduction components (used when provided; auto-computes itemized total)
    mortgage_interest: Decimal = Decimal("0")
    mortgage_loan_balance: Decimal = Decimal("0")
    salt_paid: Decimal = Decimal("0")
    charitable: Decimal = Decimal("0")
    medical_expenses: Decimal = Decimal("0")

    # Above-the-line deductions
    contributions_401k: Decimal = Decimal("0")
    ira_contributions: Decimal = Decimal("0")
    hsa_contributions: Decimal = Decimal("0")
    student_loan_interest: Decimal = Decimal("0")
    age_over_50: bool = False
    hsa_family_coverage: bool = False

    # Dependent / child credits
    num_children_under_17: int = 0
    num_other_dependents: int = 0

    # Education credits
    education_expenses: Decimal = Decimal("0")
    education_type: str = "aotc"        # "aotc" or "llc"
    num_students: int = 1

    # Withholding
    federal_withheld: Decimal = Decimal("0")
    state_withheld: Decimal = Decimal("0")
    fica_withheld: Decimal = Decimal("0")


def calculate_taxes(
    income: IncomeBreakdown,
    filing_status: FilingStatus,
    state: Optional[str] = None,
    year: int = 2025,
    # --- Legacy itemized deductions (pre-computed total) ---
    itemized_deductions: Decimal = Decimal("0"),
    # --- Itemized deduction components ---
    mortgage_interest: Decimal = Decimal("0"),
    mortgage_loan_balance: Decimal = Decimal("0"),
    salt_paid: Decimal = Decimal("0"),
    charitable: Decimal = Decimal("0"),
    medical_expenses: Decimal = Decimal("0"),
    # --- Above-the-line deductions ---
    contributions_401k: Decimal = Decimal("0"),
    ira_contributions: Decimal = Decimal("0"),
    hsa_contributions: Decimal = Decimal("0"),
    student_loan_interest: Decimal = Decimal("0"),
    age_over_50: bool = False,
    hsa_family_coverage: bool = False,
    # --- Dependent / child credits ---
    num_children_under_17: int = 0,
    num_other_dependents: int = 0,
    # --- Education credits ---
    education_expenses: Decimal = Decimal("0"),
    education_type: str = "aotc",
    num_students: int = 1,
    # --- Withholding ---
    federal_withheld: Decimal = Decimal("0"),
    state_withheld: Decimal = Decimal("0"),
    fica_withheld: Decimal = Decimal("0"),
) -> TaxSummary:
    """
    Calculate complete tax liability.

    All new deduction/credit parameters are optional (default 0/False) so
    existing callers remain fully backward-compatible.

    Args:
        income: Breakdown of income by type.
        filing_status: IRS filing status.
        state: Two-letter state code (e.g. "CA") or None.
        year: Tax year.
        itemized_deductions: Pre-computed itemized total (legacy; ignored when
            component fields are provided).
        mortgage_interest: Mortgage interest paid.
        mortgage_loan_balance: Acquisition debt balance (for $750K limit).
        salt_paid: State/local taxes paid.
        charitable: Charitable contributions.
        medical_expenses: Total medical expenses paid.
        contributions_401k: Employee 401(k) contributions.
        ira_contributions: Traditional IRA contributions.
        hsa_contributions: HSA contributions.
        student_loan_interest: Student loan interest paid.
        age_over_50: True if taxpayer (or spouse) is ≥ 50.
        hsa_family_coverage: True if enrolled in family HDHP.
        num_children_under_17: Qualifying children under 17 for CTC.
        num_other_dependents: Dependents who don't qualify for CTC.
        education_expenses: Qualified education expenses.
        education_type: "aotc" or "llc".
        num_students: Number of eligible students (AOTC).
        federal_withheld: Federal tax already withheld.
        state_withheld: State tax already withheld.
        fica_withheld: FICA already withheld (for balance comparison).

    Returns:
        Complete TaxSummary with all calculated values.
    """
    tax_year = TaxYear(year=year)
    warnings: list[str] = []

    # ========== ABOVE-THE-LINE DEDUCTIONS ==========
    atl_detail = calculate_above_the_line_deductions(
        gross_income=income.total_income,
        filing_status=filing_status,
        contributions_401k=contributions_401k,
        ira_contributions=ira_contributions,
        hsa_contributions=hsa_contributions,
        student_loan_interest=student_loan_interest,
        age_over_50=age_over_50,
        hsa_family_coverage=hsa_family_coverage,
        tax_year=tax_year,
    )

    # AGI = gross income - above-the-line deductions
    # ATL deductions reduce ordinary income first
    agi_ordinary = max(Decimal("0"), income.ordinary_income - atl_detail.total)
    agi = agi_ordinary + income.preferential_income

    # ========== ITEMIZED DEDUCTIONS ==========
    # Use component fields if any are provided; otherwise fall back to legacy total.
    has_itemized_components = any([
        mortgage_interest > 0,
        salt_paid > 0,
        charitable > 0,
        medical_expenses > 0,
    ])

    if has_itemized_components:
        itemized_detail = calculate_itemized_deductions(
            agi=agi,
            filing_status=filing_status,
            mortgage_interest=mortgage_interest,
            mortgage_loan_balance=mortgage_loan_balance,
            salt_paid=salt_paid,
            charitable=charitable,
            medical_expenses=medical_expenses,
            tax_year=tax_year,
        )
        computed_itemized = itemized_detail.total
    else:
        # Legacy path: caller supplied a pre-computed total
        computed_itemized = itemized_deductions
        itemized_detail = ItemizedDeductionsDetail(total=computed_itemized)

    # ========== FEDERAL DEDUCTIONS ==========
    standard_deduction = tax_year.get_standard_deduction(filing_status)
    deduction_used = max(standard_deduction, computed_itemized)

    # ========== FEDERAL TAXABLE INCOME ==========
    # Ordinary income minus deduction (AGI already net of above-the-line)
    taxable_ordinary = max(Decimal("0"), agi_ordinary - deduction_used)
    taxable_income = taxable_ordinary + income.preferential_income

    # ========== FEDERAL INCOME TAX (before credits) ==========
    federal_tax_ordinary = calculate_federal_tax(taxable_ordinary, filing_status)
    federal_tax_ltcg = calculate_ltcg_tax(
        income.preferential_income,
        taxable_ordinary,
        filing_status,
    )
    federal_income_tax = federal_tax_ordinary + federal_tax_ltcg

    # ========== AMT ==========
    amt_income, tentative_minimum_tax, _ = calculate_amt(
        taxable_ordinary,
        income.iso_bargain_element,
        filing_status,
        tax_year,
    )
    amt_owed = max(Decimal("0"), tentative_minimum_tax - federal_income_tax)

    if amt_owed > 0:
        warnings.append(
            f"AMT applies: ${amt_owed:,.2f} additional tax due to ISO bargain element"
        )

    # Total federal income tax before credits
    federal_tax_before_credits = federal_income_tax + amt_owed

    # ========== CREDITS ==========

    # --- Child Tax Credit / ACTC ---
    ctc, odc, actc = calculate_child_tax_credit(
        magi=agi,
        filing_status=filing_status,
        num_children_under_17=num_children_under_17,
        num_other_dependents=num_other_dependents,
        federal_tax_before_credits=federal_tax_before_credits,
        tax_year=tax_year,
    )

    # --- EITC ---
    earned_income = income.w2_wages + income.rsu_income + income.nso_income
    investment_income_for_eitc = (
        income.long_term_gains
        + income.short_term_gains
        + income.qualified_dividends
        + income.interest_income
    )
    eitc = calculate_eitc(
        earned_income=earned_income,
        agi=agi,
        filing_status=filing_status,
        num_children=num_children_under_17,
        investment_income=investment_income_for_eitc,
        tax_year=tax_year,
    )

    # --- Education Credits ---
    edu_nonrefundable, edu_refundable = calculate_education_credits(
        magi=agi,
        filing_status=filing_status,
        education_expenses=education_expenses,
        education_type=education_type,
        num_students=num_students,
        tax_year=tax_year,
    )

    # --- Apply non-refundable credits ---
    # Order: CTC → ODC → Education (non-refundable)
    tax_after_ctc = max(Decimal("0"), federal_tax_before_credits - ctc - odc)
    tax_after_edu = max(Decimal("0"), tax_after_ctc - edu_nonrefundable)
    federal_tax_total = tax_after_edu

    # Sum non-refundable credits actually applied
    total_nonrefundable_credits = (federal_tax_before_credits - federal_tax_total)

    # Refundable credits (can produce a negative net tax, i.e., a refund)
    total_refundable_credits = actc + eitc + edu_refundable
    total_credits = total_nonrefundable_credits + total_refundable_credits

    if ctc + odc > 0 or actc > 0:
        warnings.append(
            f"Child Tax Credit: ${ctc + odc:,.2f} non-refundable, "
            f"${actc:,.2f} ACTC refundable"
        )
    if eitc > 0:
        warnings.append(f"EITC: ${eitc:,.2f} (refundable)")
    if edu_nonrefundable + edu_refundable > 0:
        label = "AOTC" if education_type.lower() == "aotc" else "LLC"
        warnings.append(
            f"{label}: ${edu_nonrefundable:,.2f} non-refundable, "
            f"${edu_refundable:,.2f} refundable"
        )

    # ========== FICA ==========
    fica_wages = income.w2_wages + income.rsu_income + income.nso_income
    ss_tax, medicare_tax, additional_medicare = calculate_fica(
        fica_wages,
        filing_status,
        tax_year,
    )

    # ========== NIIT ==========
    investment_income = (
        income.long_term_gains
        + income.short_term_gains
        + income.qualified_dividends
        + income.interest_income
    )
    niit = calculate_niit(investment_income, agi, filing_status, tax_year)

    if niit > 0:
        warnings.append(f"NIIT applies: ${niit:,.2f} (3.8% on investment income)")

    # ========== STATE TAX ==========
    state_tax = Decimal("0")
    state_code = state.upper() if state else None

    if state_code == "CA":
        ca_standard = get_ca_standard_deduction(filing_status)
        ca_deduction = max(ca_standard, computed_itemized)
        ca_taxable = max(Decimal("0"), income.total_income - ca_deduction)
        state_tax = calculate_california_tax(ca_taxable, filing_status)

        sdi = calculate_sdi(income.w2_wages + income.rsu_income)
        if sdi > 0:
            warnings.append(f"CA SDI withheld: ${sdi:,.2f}")

    elif state_code == "NY":
        ny_standard = get_ny_standard_deduction(filing_status)
        ny_deduction = max(ny_standard, computed_itemized)
        ny_taxable = max(Decimal("0"), income.total_income - ny_deduction)
        state_tax = calculate_ny_tax(ny_taxable, filing_status)

    # ========== TOTALS ==========
    # Net federal = federal income tax after non-refundable credits
    # Refundable credits (ACTC, EITC, AOTC refundable) reduce balance_due further
    total_income_tax = (
        federal_tax_total
        + ss_tax
        + medicare_tax
        + additional_medicare
        + niit
        + state_tax
    )

    # Refundable credits flow through as negative tax (increase refund)
    total_tax = total_income_tax - total_refundable_credits

    # ========== RATES ==========
    if income.total_income > 0:
        effective_rate = (total_tax / income.total_income).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
    else:
        effective_rate = Decimal("0")

    federal_marginal = get_marginal_rate(taxable_ordinary, filing_status)
    if state_code == "CA":
        ca_taxable_for_marginal = max(
            Decimal("0"),
            income.total_income - get_ca_standard_deduction(filing_status)
        )
        state_marginal = get_ca_marginal_rate(ca_taxable_for_marginal, filing_status)
    elif state_code == "NY":
        ny_taxable_for_marginal = max(
            Decimal("0"),
            income.total_income - get_ny_standard_deduction(filing_status)
        )
        state_marginal = get_ny_marginal_rate(ny_taxable_for_marginal, filing_status)
    else:
        state_marginal = Decimal("0")

    marginal_rate = federal_marginal + state_marginal

    # ========== WITHHOLDING ==========
    total_withheld = federal_withheld + state_withheld + fica_withheld
    balance_due = total_tax - total_withheld

    # ========== BUILD SUMMARY ==========
    return TaxSummary(
        year=year,
        filing_status=filing_status,
        income=income,
        # Above-the-line
        above_the_line_deductions=atl_detail,
        agi=agi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        # Deductions
        standard_deduction=standard_deduction,
        itemized_deductions=computed_itemized,
        itemized_deductions_detail=itemized_detail,
        deduction_used=deduction_used,
        # Taxable income
        taxable_income=taxable_income,
        # Federal tax
        federal_tax_on_ordinary=federal_tax_ordinary,
        federal_tax_on_ltcg=federal_tax_ltcg,
        federal_tax_total=federal_tax_total,
        # AMT
        amt_income=amt_income,
        tentative_minimum_tax=tentative_minimum_tax,
        amt_owed=amt_owed,
        # Credits
        child_tax_credit=ctc,
        other_dependent_credit=odc,
        actc=actc,
        eitc=eitc,
        education_credit=edu_nonrefundable,
        education_credit_refundable=edu_refundable,
        total_credits=total_credits.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        # FICA
        social_security_tax=ss_tax,
        medicare_tax=medicare_tax,
        additional_medicare_tax=additional_medicare,
        niit=niit,
        # State
        state_tax=state_tax,
        state_code=state_code,
        # Totals
        total_tax=total_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        effective_rate=effective_rate,
        marginal_rate=marginal_rate,
        total_withheld=total_withheld,
        balance_due=balance_due.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        warnings=warnings,
    )


def format_tax_summary(summary: TaxSummary) -> str:
    """
    Format a TaxSummary as a human-readable string.

    Args:
        summary: TaxSummary to format.

    Returns:
        Formatted multi-line string.
    """
    lines = [
        "=" * 60,
        f"TAX SUMMARY - {summary.year}",
        "=" * 60,
        "",
        "INCOME",
        "-" * 40,
        f"  W-2 Wages:              ${summary.income.w2_wages:>12,.2f}",
    ]

    if summary.income.rsu_income > 0:
        lines.append(f"  RSU Income:             ${summary.income.rsu_income:>12,.2f}")
    if summary.income.nso_income > 0:
        lines.append(f"  NSO Income:             ${summary.income.nso_income:>12,.2f}")
    if summary.income.short_term_gains > 0:
        lines.append(f"  Short-Term Gains:       ${summary.income.short_term_gains:>12,.2f}")
    if summary.income.long_term_gains > 0:
        lines.append(f"  Long-Term Gains:        ${summary.income.long_term_gains:>12,.2f}")
    if summary.income.qualified_dividends > 0:
        lines.append(f"  Qualified Dividends:    ${summary.income.qualified_dividends:>12,.2f}")
    if summary.income.interest_income > 0:
        lines.append(f"  Interest Income:        ${summary.income.interest_income:>12,.2f}")

    lines.extend([
        f"  -----------------------------------------",
        f"  TOTAL INCOME:           ${summary.income.total_income:>12,.2f}",
    ])

    atl = summary.above_the_line_deductions
    if atl.total > 0:
        lines.extend([
            "",
            "ABOVE-THE-LINE DEDUCTIONS",
            "-" * 40,
        ])
        if atl.contributions_401k > 0:
            lines.append(f"  401(k):                 ${atl.contributions_401k:>12,.2f}")
        if atl.ira_contributions > 0:
            lines.append(f"  Traditional IRA:        ${atl.ira_contributions:>12,.2f}")
        if atl.hsa_contributions > 0:
            lines.append(f"  HSA:                    ${atl.hsa_contributions:>12,.2f}")
        if atl.student_loan_interest > 0:
            lines.append(f"  Student Loan Interest:  ${atl.student_loan_interest:>12,.2f}")
        lines.extend([
            f"  -----------------------------------------",
            f"  AGI:                    ${summary.agi:>12,.2f}",
        ])

    lines.extend([
        "",
        "DEDUCTIONS",
        "-" * 40,
        f"  Standard Deduction:     ${summary.standard_deduction:>12,.2f}",
    ])

    detail = summary.itemized_deductions_detail
    if detail.total > 0:
        lines.append(f"  Itemized Deductions:    ${detail.total:>12,.2f}")
        if detail.mortgage_interest > 0:
            lines.append(f"    Mortgage Interest:    ${detail.mortgage_interest:>12,.2f}")
        if detail.salt > 0:
            lines.append(f"    SALT (capped):        ${detail.salt:>12,.2f}")
        if detail.charitable > 0:
            lines.append(f"    Charitable:           ${detail.charitable:>12,.2f}")
        if detail.medical > 0:
            lines.append(f"    Medical (net):        ${detail.medical:>12,.2f}")

    lines.extend([
        f"  Deduction Used:         ${summary.deduction_used:>12,.2f}",
        f"  -----------------------------------------",
        f"  TAXABLE INCOME:         ${summary.taxable_income:>12,.2f}",
        "",
        "FEDERAL TAX",
        "-" * 40,
        f"  Tax on Ordinary Income: ${summary.federal_tax_on_ordinary:>12,.2f}",
    ])

    if summary.federal_tax_on_ltcg > 0:
        lines.append(f"  Tax on LTCG/QDIV:       ${summary.federal_tax_on_ltcg:>12,.2f}")

    if summary.amt_owed > 0:
        lines.append(f"  AMT:                    ${summary.amt_owed:>12,.2f}")

    if summary.total_credits > 0:
        lines.extend([
            "",
            "CREDITS",
            "-" * 40,
        ])
        if summary.child_tax_credit > 0 or summary.other_dependent_credit > 0:
            lines.append(
                f"  Child/Dep Credit:       ${summary.child_tax_credit + summary.other_dependent_credit:>12,.2f}"
            )
        if summary.actc > 0:
            lines.append(f"  ACTC (refundable):      ${summary.actc:>12,.2f}")
        if summary.eitc > 0:
            lines.append(f"  EITC (refundable):      ${summary.eitc:>12,.2f}")
        if summary.education_credit > 0:
            lines.append(f"  Education Credit:       ${summary.education_credit:>12,.2f}")
        if summary.education_credit_refundable > 0:
            lines.append(f"  Education (refundable): ${summary.education_credit_refundable:>12,.2f}")
        lines.append(f"  -----------------------------------------")
        lines.append(f"  TOTAL CREDITS:          ${summary.total_credits:>12,.2f}")

    lines.extend([
        "",
        "  FEDERAL INCOME TAX:     "
        f"${summary.federal_tax_on_ordinary + summary.federal_tax_on_ltcg + summary.amt_owed:>12,.2f}",
        f"  After Credits:          ${summary.federal_tax_total:>12,.2f}",
        "",
        "PAYROLL TAXES",
        "-" * 40,
        f"  Social Security:        ${summary.social_security_tax:>12,.2f}",
        f"  Medicare:               ${summary.medicare_tax:>12,.2f}",
    ])

    if summary.additional_medicare_tax > 0:
        lines.append(f"  Additional Medicare:    ${summary.additional_medicare_tax:>12,.2f}")

    if summary.niit > 0:
        lines.append(f"  NIIT (3.8%):            ${summary.niit:>12,.2f}")

    if summary.state_code:
        lines.extend([
            "",
            f"STATE TAX ({summary.state_code})",
            "-" * 40,
            f"  State Income Tax:       ${summary.state_tax:>12,.2f}",
        ])

    lines.extend([
        "",
        "TOTALS",
        "-" * 40,
        f"  TOTAL TAX:              ${summary.total_tax:>12,.2f}",
        f"  Effective Rate:         {summary.effective_rate * 100:>11.2f}%",
        f"  Marginal Rate:          {summary.marginal_rate * 100:>11.2f}%",
    ])

    if summary.total_withheld > 0 or summary.balance_due != summary.total_tax:
        lines.extend([
            "",
            "WITHHOLDING",
            "-" * 40,
            f"  Total Withheld:         ${summary.total_withheld:>12,.2f}",
        ])
        if summary.balance_due > 0:
            lines.append(f"  BALANCE DUE:            ${summary.balance_due:>12,.2f}")
        else:
            lines.append(f"  REFUND:                 ${-summary.balance_due:>12,.2f}")

    if summary.warnings:
        lines.extend([
            "",
            "WARNINGS / NOTES",
            "-" * 40,
        ])
        for warning in summary.warnings:
            lines.append(f"  ⚠ {warning}")

    lines.append("=" * 60)

    return "\n".join(lines)
