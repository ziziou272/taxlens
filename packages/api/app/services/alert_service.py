"""Alert service — delegates to taxlens_engine red_flags."""
from decimal import Decimal
from typing import Optional

from taxlens_engine.red_flags import analyze_red_flags

from app.schemas.alert import AlertCheckInput, AlertCheckResponse, AlertResponse


def check_alerts(inp: AlertCheckInput) -> AlertCheckResponse:
    """Run red flag analysis on provided tax data."""
    report = analyze_red_flags(
        total_income=Decimal(str(inp.total_income)),
        total_tax_liability=Decimal(str(inp.total_tax_liability)),
        total_withheld=Decimal(str(inp.total_withheld)),
        long_term_gains=Decimal(str(inp.long_term_gains)),
        short_term_gains=Decimal(str(inp.short_term_gains)),
        rsu_income=Decimal(str(inp.rsu_income)),
        iso_bargain_element=Decimal(str(inp.iso_bargain_element)),
        filing_status=inp.filing_status,
        state=inp.state,
        prior_year_tax=Decimal(str(inp.prior_year_tax)) if inp.prior_year_tax is not None else None,
    )

    alerts = [
        AlertResponse(
            severity=a.severity.value,
            category=a.category.value,
            title=a.title,
            message=a.message,
            amount=float(a.amount) if a.amount is not None else None,
            action_required=a.action_required,
            deadline=a.deadline,
        )
        for a in report.alerts
    ]

    return AlertCheckResponse(
        summary=report.summary,
        alerts=alerts,
        has_critical=report.has_critical,
    )
