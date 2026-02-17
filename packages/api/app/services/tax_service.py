"""Tax calculation service — delegates to taxlens_engine."""
from decimal import Decimal

from taxlens_engine.models import FilingStatus, IncomeBreakdown
from taxlens_engine.calculator import calculate_taxes

from app.schemas.tax import (
    TaxInput,
    TaxBreakdownResponse,
    WithholdingGapInput,
    WithholdingGapResponse,
    ItemizedDeductionsDetailResponse,
    AboveTheLineDeductionsResponse,
)


def _to_filing_status(s: str) -> FilingStatus:
    return FilingStatus(s)


def _d(value: float) -> Decimal:
    """Convert float to Decimal safely."""
    return Decimal(str(value))


def calculate(inp: TaxInput) -> TaxBreakdownResponse:
    """Run full tax calculation via engine."""
    # Compute ISO/NSO derived income
    nso_income = sum(
        (e.fmv_at_exercise - e.strike_price) * e.shares for e in inp.nso_exercises
    )
    iso_bargain = sum(
        (e.fmv_at_exercise - e.strike_price) * e.shares for e in inp.iso_exercises
    )

    income = IncomeBreakdown(
        w2_wages=_d(inp.wages),
        rsu_income=_d(inp.rsu_income),
        nso_income=_d(nso_income),
        short_term_gains=_d(inp.capital_gains_short),
        long_term_gains=_d(inp.capital_gains_long),
        qualified_dividends=_d(inp.qualified_dividends),
        interest_income=_d(inp.interest_income),
        iso_bargain_element=_d(iso_bargain),
    )

    summary = calculate_taxes(
        income=income,
        filing_status=_to_filing_status(inp.filing_status),
        state=inp.state,
        # Legacy itemized total (ignored when components provided)
        itemized_deductions=_d(inp.itemized_deductions or 0),
        # Itemized components
        mortgage_interest=_d(inp.mortgage_interest),
        mortgage_loan_balance=_d(inp.mortgage_loan_balance),
        salt_paid=_d(inp.salt_paid),
        charitable=_d(inp.charitable),
        medical_expenses=_d(inp.medical_expenses),
        # Above-the-line deductions
        contributions_401k=_d(inp.contributions_401k),
        ira_contributions=_d(inp.ira_contributions),
        hsa_contributions=_d(inp.hsa_contributions),
        student_loan_interest=_d(inp.student_loan_interest),
        age_over_50=inp.age_over_50,
        hsa_family_coverage=inp.hsa_family_coverage,
        # Dependents / credits
        num_children_under_17=inp.num_children_under_17,
        num_other_dependents=inp.num_other_dependents,
        # Education credits
        education_expenses=_d(inp.education_expenses),
        education_type=inp.education_type,
        num_students=inp.num_students,
        # Withholding
        federal_withheld=_d(inp.federal_withheld),
        state_withheld=_d(inp.state_withheld),
    )

    atl = summary.above_the_line_deductions
    detail = summary.itemized_deductions_detail

    return TaxBreakdownResponse(
        year=summary.year,
        filing_status=summary.filing_status.value,
        total_income=float(summary.income.total_income),
        agi=float(summary.agi),
        taxable_income=float(summary.taxable_income),
        deduction_used=float(summary.deduction_used),
        # Above-the-line deductions
        above_the_line_deductions=AboveTheLineDeductionsResponse(
            contributions_401k=float(atl.contributions_401k),
            ira_contributions=float(atl.ira_contributions),
            hsa_contributions=float(atl.hsa_contributions),
            student_loan_interest=float(atl.student_loan_interest),
            total=float(atl.total),
        ),
        # Itemized deductions
        itemized_deductions_detail=ItemizedDeductionsDetailResponse(
            mortgage_interest=float(detail.mortgage_interest),
            salt=float(detail.salt),
            salt_paid=float(detail.salt_paid),
            charitable=float(detail.charitable),
            medical=float(detail.medical),
            medical_paid=float(detail.medical_paid),
            total=float(detail.total),
        ),
        # Federal tax
        federal_tax=float(summary.federal_tax_total),
        federal_tax_on_ordinary=float(summary.federal_tax_on_ordinary),
        federal_tax_on_ltcg=float(summary.federal_tax_on_ltcg),
        amt_owed=float(summary.amt_owed),
        # Credits
        child_tax_credit=float(summary.child_tax_credit),
        other_dependent_credit=float(summary.other_dependent_credit),
        actc=float(summary.actc),
        eitc=float(summary.eitc),
        education_credit=float(summary.education_credit),
        education_credit_refundable=float(summary.education_credit_refundable),
        total_credits=float(summary.total_credits),
        # Payroll
        social_security_tax=float(summary.social_security_tax),
        medicare_tax=float(summary.medicare_tax),
        additional_medicare_tax=float(summary.additional_medicare_tax),
        niit=float(summary.niit),
        # State
        state_tax=float(summary.state_tax),
        state_code=summary.state_code,
        # Totals
        total_tax=float(summary.total_tax),
        effective_rate=float(summary.effective_rate),
        marginal_rate=float(summary.marginal_rate),
        balance_due=float(summary.balance_due),
        warnings=summary.warnings,
    )


def withholding_gap(inp: WithholdingGapInput) -> WithholdingGapResponse:
    """Compare YTD withholding vs projected liability."""
    income = IncomeBreakdown(
        w2_wages=_d(inp.wages),
        rsu_income=_d(inp.rsu_income),
        long_term_gains=_d(inp.capital_gains_long),
    )
    summary = calculate_taxes(
        income=income,
        filing_status=_to_filing_status(inp.filing_status),
        state=inp.state,
    )
    projected = float(summary.total_tax)
    ytd = inp.ytd_federal_withheld + inp.ytd_state_withheld
    gap = projected - ytd
    pct = (gap / projected * 100) if projected > 0 else 0
    quarterly = max(0, gap) / 4

    warnings = []
    if gap > 1000:
        warnings.append(f"Projected shortfall of ${gap:,.2f}. Consider estimated payments.")

    return WithholdingGapResponse(
        projected_total_tax=projected,
        ytd_withheld=ytd,
        gap=gap,
        gap_percentage=round(pct, 2),
        quarterly_payment_needed=round(quarterly, 2),
        warnings=warnings,
    )
