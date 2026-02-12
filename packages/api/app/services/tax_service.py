"""Tax calculation service — delegates to taxlens_engine."""
from decimal import Decimal

from taxlens_engine.models import FilingStatus, IncomeBreakdown
from taxlens_engine.calculator import calculate_taxes

from app.schemas.tax import TaxInput, TaxBreakdownResponse, WithholdingGapInput, WithholdingGapResponse


def _to_filing_status(s: str) -> FilingStatus:
    return FilingStatus(s)


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
        w2_wages=Decimal(str(inp.wages)),
        rsu_income=Decimal(str(inp.rsu_income)),
        nso_income=Decimal(str(nso_income)),
        short_term_gains=Decimal(str(inp.capital_gains_short)),
        long_term_gains=Decimal(str(inp.capital_gains_long)),
        qualified_dividends=Decimal(str(inp.qualified_dividends)),
        interest_income=Decimal(str(inp.interest_income)),
        iso_bargain_element=Decimal(str(iso_bargain)),
    )

    summary = calculate_taxes(
        income=income,
        filing_status=_to_filing_status(inp.filing_status),
        state=inp.state,
        itemized_deductions=Decimal(str(inp.itemized_deductions or 0)),
        federal_withheld=Decimal(str(inp.federal_withheld)),
        state_withheld=Decimal(str(inp.state_withheld)),
    )

    return TaxBreakdownResponse(
        year=summary.year,
        filing_status=summary.filing_status.value,
        total_income=float(summary.income.total_income),
        taxable_income=float(summary.taxable_income),
        federal_tax=float(summary.federal_tax_total),
        federal_tax_on_ordinary=float(summary.federal_tax_on_ordinary),
        federal_tax_on_ltcg=float(summary.federal_tax_on_ltcg),
        amt_owed=float(summary.amt_owed),
        social_security_tax=float(summary.social_security_tax),
        medicare_tax=float(summary.medicare_tax),
        additional_medicare_tax=float(summary.additional_medicare_tax),
        niit=float(summary.niit),
        state_tax=float(summary.state_tax),
        state_code=summary.state_code,
        total_tax=float(summary.total_tax),
        effective_rate=float(summary.effective_rate),
        marginal_rate=float(summary.marginal_rate),
        deduction_used=float(summary.deduction_used),
        balance_due=float(summary.balance_due),
        warnings=summary.warnings,
    )


def withholding_gap(inp: WithholdingGapInput) -> WithholdingGapResponse:
    """Compare YTD withholding vs projected liability."""
    income = IncomeBreakdown(
        w2_wages=Decimal(str(inp.wages)),
        rsu_income=Decimal(str(inp.rsu_income)),
        long_term_gains=Decimal(str(inp.capital_gains_long)),
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
