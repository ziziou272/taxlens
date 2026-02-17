"""
Complete tax calculator for TaxLens.

Integrates federal, state, and payroll taxes into a comprehensive summary.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from pydantic import BaseModel

from taxlens_engine.models import (
    FilingStatus,
    IncomeBreakdown,
    TaxSummary,
    TaxYear,
)
from taxlens_engine.federal import (
    calculate_federal_tax,
    calculate_ltcg_tax,
    calculate_amt,
    calculate_fica,
    calculate_niit,
    get_marginal_rate,
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
    itemized_deductions: Decimal = Decimal("0")
    federal_withheld: Decimal = Decimal("0")
    state_withheld: Decimal = Decimal("0")
    fica_withheld: Decimal = Decimal("0")


def calculate_taxes(
    income: IncomeBreakdown,
    filing_status: FilingStatus,
    state: Optional[str] = None,
    year: int = 2025,
    itemized_deductions: Decimal = Decimal("0"),
    federal_withheld: Decimal = Decimal("0"),
    state_withheld: Decimal = Decimal("0"),
    fica_withheld: Decimal = Decimal("0"),
) -> TaxSummary:
    """
    Calculate complete tax liability.
    
    Args:
        income: Breakdown of income by type
        filing_status: IRS filing status
        state: Two-letter state code (e.g., "CA") or None
        year: Tax year
        itemized_deductions: Itemized deductions (if any)
        federal_withheld: Federal tax already withheld
        state_withheld: State tax already withheld
        fica_withheld: FICA already withheld (for comparison only)
        
    Returns:
        Complete TaxSummary with all calculated values
    """
    tax_year = TaxYear(year=year)
    warnings: list[str] = []
    
    # ========== FEDERAL DEDUCTIONS ==========
    standard_deduction = tax_year.get_standard_deduction(filing_status)
    deduction_used = max(standard_deduction, itemized_deductions)
    
    # ========== FEDERAL TAXABLE INCOME ==========
    # Ordinary income minus deduction
    taxable_ordinary = max(Decimal("0"), income.ordinary_income - deduction_used)
    
    # Total federal taxable income (including preferential)
    taxable_income = taxable_ordinary + income.preferential_income
    
    # ========== FEDERAL INCOME TAX ==========
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
    
    federal_tax_total = federal_income_tax + amt_owed
    
    # ========== FICA ==========
    # FICA applies to W-2 wages (RSU income already had FICA withheld at vesting)
    fica_wages = income.w2_wages + income.rsu_income + income.nso_income
    ss_tax, medicare_tax, additional_medicare = calculate_fica(
        fica_wages,
        filing_status,
        tax_year,
    )
    
    # ========== NIIT ==========
    investment_income = (
        income.long_term_gains +
        income.short_term_gains +
        income.qualified_dividends +
        income.interest_income
    )
    magi = income.total_income  # Simplified; MAGI can have adjustments
    niit = calculate_niit(investment_income, magi, filing_status, tax_year)
    
    if niit > 0:
        warnings.append(
            f"NIIT applies: ${niit:,.2f} (3.8% on investment income)"
        )
    
    # ========== STATE TAX ==========
    state_tax = Decimal("0")
    state_code = state.upper() if state else None
    
    if state_code == "CA":
        # California uses its own standard deduction
        ca_standard = get_ca_standard_deduction(filing_status)
        ca_deduction = max(ca_standard, itemized_deductions)
        ca_taxable = max(Decimal("0"), income.total_income - ca_deduction)
        state_tax = calculate_california_tax(ca_taxable, filing_status)

        # SDI is withheld from wages (not additional tax owed) — reported in warnings
        # As of 2024, CA SDI applies to all wages with no wage cap.
        sdi = calculate_sdi(income.w2_wages + income.rsu_income)
        if sdi > 0:
            warnings.append(f"CA SDI withheld: ${sdi:,.2f}")

    elif state_code == "NY":
        # New York uses its own standard deduction
        ny_standard = get_ny_standard_deduction(filing_status)
        ny_deduction = max(ny_standard, itemized_deductions)
        ny_taxable = max(Decimal("0"), income.total_income - ny_deduction)
        state_tax = calculate_ny_tax(ny_taxable, filing_status)
    
    # ========== TOTALS ==========
    total_tax = (
        federal_tax_total +
        ss_tax +
        medicare_tax +
        additional_medicare +
        niit +
        state_tax
    )
    
    # ========== RATES ==========
    if income.total_income > 0:
        effective_rate = (total_tax / income.total_income).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
    else:
        effective_rate = Decimal("0")
    
    # Marginal rate = federal + state
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
        standard_deduction=standard_deduction,
        itemized_deductions=itemized_deductions,
        deduction_used=deduction_used,
        taxable_income=taxable_income,
        federal_tax_on_ordinary=federal_tax_ordinary,
        federal_tax_on_ltcg=federal_tax_ltcg,
        federal_tax_total=federal_tax_total,
        amt_income=amt_income,
        tentative_minimum_tax=tentative_minimum_tax,
        amt_owed=amt_owed,
        social_security_tax=ss_tax,
        medicare_tax=medicare_tax,
        additional_medicare_tax=additional_medicare,
        niit=niit,
        state_tax=state_tax,
        state_code=state_code,
        total_tax=total_tax,
        effective_rate=effective_rate,
        marginal_rate=marginal_rate,
        total_withheld=total_withheld,
        balance_due=balance_due,
        warnings=warnings,
    )


def format_tax_summary(summary: TaxSummary) -> str:
    """
    Format a TaxSummary as a human-readable string.
    
    Args:
        summary: TaxSummary to format
        
    Returns:
        Formatted multi-line string
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
        "",
        "DEDUCTIONS",
        "-" * 40,
        f"  Standard Deduction:     ${summary.standard_deduction:>12,.2f}",
    ])
    
    if summary.itemized_deductions > 0:
        lines.append(f"  Itemized Deductions:    ${summary.itemized_deductions:>12,.2f}")
    
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
    
    lines.extend([
        f"  -----------------------------------------",
        f"  FEDERAL INCOME TAX:     ${summary.federal_tax_total:>12,.2f}",
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
            "WARNINGS",
            "-" * 40,
        ])
        for warning in summary.warnings:
            lines.append(f"  ⚠ {warning}")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
