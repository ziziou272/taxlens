"""
Red Flags / Warning System for TaxLens.

Detects potential tax issues before they become expensive problems:
- Underwithholding alerts
- AMT trigger warnings
- State-specific thresholds (WA capital gains)
- Estimated payment requirements
- Large equity event impacts
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional


class AlertSeverity(str, Enum):
    """Severity level for tax alerts."""
    INFO = "info"           # FYI, good to know
    WARNING = "warning"     # Should review
    CRITICAL = "critical"   # Immediate action needed


class AlertCategory(str, Enum):
    """Category of tax alert."""
    WITHHOLDING = "withholding"
    AMT = "amt"
    STATE_TAX = "state_tax"
    ESTIMATED_PAYMENTS = "estimated_payments"
    PENALTY_RISK = "penalty_risk"
    PLANNING = "planning"


@dataclass
class TaxAlert:
    """A single tax alert/warning."""
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    amount: Optional[Decimal] = None
    action_required: Optional[str] = None
    deadline: Optional[str] = None


@dataclass
class RedFlagReport:
    """Complete red flag analysis report."""
    alerts: list[TaxAlert] = field(default_factory=list)
    summary: str = ""
    
    @property
    def critical_alerts(self) -> list[TaxAlert]:
        """Get critical severity alerts."""
        return [a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]
    
    @property
    def warning_alerts(self) -> list[TaxAlert]:
        """Get warning severity alerts."""
        return [a for a in self.alerts if a.severity == AlertSeverity.WARNING]
    
    @property
    def has_critical(self) -> bool:
        """Check if any critical alerts exist."""
        return len(self.critical_alerts) > 0
    
    def add_alert(self, alert: TaxAlert):
        """Add an alert to the report."""
        self.alerts.append(alert)


# ============================================================
# Underwithholding Checks
# ============================================================

def check_underwithholding(
    total_tax_liability: Decimal,
    total_withheld: Decimal,
    prior_year_tax: Optional[Decimal] = None,
) -> list[TaxAlert]:
    """
    Check for underwithholding and potential penalties.
    
    IRS safe harbor rules:
    - Owe < $1,000 at filing = no penalty
    - Withheld >= 90% of current year tax = no penalty
    - Withheld >= 100% of prior year tax = no penalty
      (110% if prior year AGI > $150,000)
    
    Args:
        total_tax_liability: Current year estimated total tax
        total_withheld: Total tax already withheld (fed + state)
        prior_year_tax: Prior year's total tax (for safe harbor)
        
    Returns:
        List of relevant alerts
    """
    alerts = []
    
    balance_due = total_tax_liability - total_withheld
    
    if balance_due <= Decimal("0"):
        # Getting a refund, no underwithholding
        return alerts
    
    # Check $1,000 threshold
    if balance_due < Decimal("1000"):
        alerts.append(TaxAlert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.WITHHOLDING,
            title="Small Balance Due",
            message=f"Balance due of ${balance_due:,.2f} is under $1,000 - no penalty expected.",
            amount=balance_due,
        ))
        return alerts
    
    # Calculate withholding percentage
    if total_tax_liability > 0:
        withholding_pct = (total_withheld / total_tax_liability) * 100
    else:
        withholding_pct = Decimal("100")
    
    # Check 90% rule
    if withholding_pct < Decimal("90"):
        alerts.append(TaxAlert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.WITHHOLDING,
            title="Significant Underwithholding",
            message=f"Only {withholding_pct:.1f}% of tax liability withheld (90% required). "
                    f"Balance due: ${balance_due:,.2f}",
            amount=balance_due,
            action_required="Consider making an estimated tax payment to avoid penalties.",
            deadline="Quarterly estimated tax deadlines: Apr 15, Jun 15, Sep 15, Jan 15",
        ))
    elif withholding_pct < Decimal("100"):
        alerts.append(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.WITHHOLDING,
            title="Potential Underwithholding",
            message=f"Withholding covers {withholding_pct:.1f}% of estimated tax. "
                    f"Balance due: ${balance_due:,.2f}",
            amount=balance_due,
            action_required="Review withholding or consider estimated payment.",
        ))
    
    # Check prior year safe harbor
    if prior_year_tax is not None and prior_year_tax > 0:
        if total_withheld >= prior_year_tax:
            alerts.append(TaxAlert(
                severity=AlertSeverity.INFO,
                category=AlertCategory.WITHHOLDING,
                title="Prior Year Safe Harbor Met",
                message=f"Withholding (${total_withheld:,.2f}) exceeds prior year tax "
                        f"(${prior_year_tax:,.2f}). No penalty expected.",
                amount=balance_due,
            ))
        elif total_withheld >= prior_year_tax * Decimal("0.9"):
            # Close to safe harbor
            alerts.append(TaxAlert(
                severity=AlertSeverity.INFO,
                category=AlertCategory.WITHHOLDING,
                title="Near Prior Year Safe Harbor",
                message=f"Withholding is {(total_withheld/prior_year_tax)*100:.1f}% of prior year tax. "
                        f"110% safe harbor may apply if prior AGI > $150K.",
            ))
    
    return alerts


def check_rsu_underwithholding(
    rsu_income: Decimal,
    supplemental_withheld: Decimal,
    actual_marginal_rate: Decimal,
    state: str = "CA",
) -> list[TaxAlert]:
    """
    Check if RSU withholding is sufficient.
    
    Common issue: RSU withholding uses flat 22% federal rate,
    but actual marginal rate may be 32-37%+.
    
    Args:
        rsu_income: Total RSU vesting income
        supplemental_withheld: Tax withheld from RSU (usually 22% + state)
        actual_marginal_rate: Your actual combined marginal rate
        state: State code for state-specific rates
        
    Returns:
        List of alerts
    """
    alerts = []
    
    if rsu_income <= 0:
        return alerts
    
    # Typical supplemental rates
    federal_supplemental = Decimal("0.22")
    state_rates = {
        "CA": Decimal("0.1023"),
        "NY": Decimal("0.0685"),
        "WA": Decimal("0"),  # No state income tax
        "TX": Decimal("0"),
    }
    state_rate = state_rates.get(state, Decimal("0.05"))
    fica_rate = Decimal("0.0765")  # Simplified
    
    typical_withholding_rate = federal_supplemental + state_rate + fica_rate
    
    # Check if actual marginal rate is much higher
    if actual_marginal_rate > typical_withholding_rate + Decimal("0.05"):
        shortfall_rate = actual_marginal_rate - typical_withholding_rate
        estimated_shortfall = rsu_income * shortfall_rate
        
        alerts.append(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.WITHHOLDING,
            title="RSU Withholding Gap",
            message=f"RSU withholding rate (~{typical_withholding_rate*100:.1f}%) is lower than "
                    f"your marginal rate (~{actual_marginal_rate*100:.1f}%). "
                    f"Estimated shortfall: ${estimated_shortfall:,.2f}",
            amount=estimated_shortfall,
            action_required="Consider increasing W-4 withholding or making estimated payments.",
        ))
    
    return alerts


# ============================================================
# AMT Checks
# ============================================================

def check_amt_trigger(
    regular_taxable_income: Decimal,
    iso_bargain_element: Decimal,
    filing_status: str = "single",
) -> list[TaxAlert]:
    """
    Check if ISO exercise will trigger AMT.
    
    Args:
        regular_taxable_income: Regular taxable income
        iso_bargain_element: ISO bargain element from exercise
        filing_status: "single" or "married_jointly"
        
    Returns:
        List of AMT-related alerts
    """
    alerts = []
    
    if iso_bargain_element <= 0:
        return alerts
    
    # 2025 AMT exemptions
    if filing_status == "married_jointly":
        exemption = Decimal("137000")
        phaseout_start = Decimal("1252700")
    else:
        exemption = Decimal("88100")
        phaseout_start = Decimal("626350")
    
    # AMT income
    amt_income = regular_taxable_income + iso_bargain_element
    
    # Check if will trigger AMT
    if amt_income > exemption:
        # Simplified AMT estimate
        amt_taxable = amt_income - exemption
        if amt_income > phaseout_start:
            # Exemption phases out
            reduction = (amt_income - phaseout_start) * Decimal("0.25")
            exemption = max(Decimal("0"), exemption - reduction)
            amt_taxable = amt_income - exemption
        
        # AMT rate (simplified)
        estimated_amt = amt_taxable * Decimal("0.26")
        
        severity = AlertSeverity.WARNING
        if iso_bargain_element > Decimal("100000"):
            severity = AlertSeverity.CRITICAL
        
        alerts.append(TaxAlert(
            severity=severity,
            category=AlertCategory.AMT,
            title="ISO Exercise May Trigger AMT",
            message=f"ISO bargain element of ${iso_bargain_element:,.2f} creates AMT income "
                    f"of ${amt_income:,.2f}. Estimated additional AMT: ${estimated_amt:,.2f}",
            amount=estimated_amt,
            action_required="Consider spreading ISO exercises across multiple tax years. "
                           "Consult a tax advisor before exercising.",
        ))
        
        # Warn about potential AMT trap
        if iso_bargain_element > Decimal("50000"):
            alerts.append(TaxAlert(
                severity=AlertSeverity.WARNING,
                category=AlertCategory.AMT,
                title="AMT Trap Risk",
                message="Large ISO exercises can create 'paper' tax liability. If stock drops "
                        "before sale, you may owe AMT on gains that no longer exist.",
                action_required="Plan for potential stock price volatility. Consider same-year "
                               "disqualifying disposition to eliminate AMT.",
            ))
    
    return alerts


# ============================================================
# State-Specific Checks
# ============================================================

def check_washington_capital_gains(
    long_term_capital_gains: Decimal,
) -> list[TaxAlert]:
    """
    Check for Washington State capital gains tax.
    
    WA has a 7% tax on long-term capital gains over $262,000 (2024).
    
    Args:
        long_term_capital_gains: Total LTCG for the year
        
    Returns:
        Alerts if WA capital gains tax applies
    """
    alerts = []
    
    # 2024 threshold (adjust for inflation)
    wa_threshold = Decimal("262000")
    wa_rate = Decimal("0.07")
    
    if long_term_capital_gains > wa_threshold:
        excess = long_term_capital_gains - wa_threshold
        wa_tax = (excess * wa_rate).quantize(Decimal("0.01"))
        
        alerts.append(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.STATE_TAX,
            title="Washington State Capital Gains Tax",
            message=f"LTCG of ${long_term_capital_gains:,.2f} exceeds WA threshold of "
                    f"${wa_threshold:,.2f}. WA tax due: ${wa_tax:,.2f}",
            amount=wa_tax,
            action_required="File WA capital gains excise tax return. Consider timing of "
                           "future sales to manage threshold.",
        ))
    elif long_term_capital_gains > wa_threshold * Decimal("0.8"):
        # Approaching threshold
        remaining = wa_threshold - long_term_capital_gains
        alerts.append(TaxAlert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.STATE_TAX,
            title="Approaching WA Capital Gains Threshold",
            message=f"LTCG of ${long_term_capital_gains:,.2f} is approaching WA threshold. "
                    f"${remaining:,.2f} remaining before 7% tax applies.",
            action_required="Consider deferring additional capital gains to next year.",
        ))
    
    return alerts


def check_niit_threshold(
    magi: Decimal,
    investment_income: Decimal,
    filing_status: str = "single",
) -> list[TaxAlert]:
    """
    Check for Net Investment Income Tax (NIIT).
    
    3.8% tax on lesser of:
    - Net investment income, or
    - MAGI over threshold
    
    Args:
        magi: Modified Adjusted Gross Income
        investment_income: Net investment income
        filing_status: Filing status
        
    Returns:
        NIIT alerts
    """
    alerts = []
    
    thresholds = {
        "single": Decimal("200000"),
        "married_jointly": Decimal("250000"),
        "married_separately": Decimal("125000"),
        "head_of_household": Decimal("200000"),
    }
    
    threshold = thresholds.get(filing_status, Decimal("200000"))
    
    if magi > threshold and investment_income > 0:
        excess_magi = magi - threshold
        niit_base = min(investment_income, excess_magi)
        niit = (niit_base * Decimal("0.038")).quantize(Decimal("0.01"))
        
        alerts.append(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.PLANNING,
            title="NIIT Applies",
            message=f"MAGI of ${magi:,.2f} exceeds ${threshold:,.2f} threshold. "
                    f"NIIT of ${niit:,.2f} applies to investment income.",
            amount=niit,
            action_required="NIIT cannot be reduced by withholding. Ensure adequate "
                           "estimated payments or adjust W-4 for additional withholding.",
        ))
    
    return alerts


# ============================================================
# Estimated Payment Checks
# ============================================================

def check_estimated_payments_required(
    balance_due: Decimal,
    income_sources: dict,
) -> list[TaxAlert]:
    """
    Check if estimated tax payments are required.
    
    Required if:
    - Will owe >= $1,000 at filing
    - Significant non-wage income (investments, equity sales)
    
    Args:
        balance_due: Expected balance due at filing
        income_sources: Dict with income by source
        
    Returns:
        Estimated payment alerts
    """
    alerts = []
    
    if balance_due < Decimal("1000"):
        return alerts
    
    # Check for significant non-wage income
    non_wage_income = (
        income_sources.get("capital_gains", Decimal("0")) +
        income_sources.get("dividends", Decimal("0")) +
        income_sources.get("interest", Decimal("0")) +
        income_sources.get("other", Decimal("0"))
    )
    
    if non_wage_income > Decimal("10000"):
        # Significant non-wage income
        quarterly_payment = (balance_due / 4).quantize(Decimal("0.01"))
        
        alerts.append(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.ESTIMATED_PAYMENTS,
            title="Estimated Payments Likely Required",
            message=f"Balance due of ${balance_due:,.2f} with significant investment income "
                    f"(${non_wage_income:,.2f}) likely requires quarterly estimated payments.",
            amount=quarterly_payment,
            action_required=f"Consider making quarterly payments of ~${quarterly_payment:,.2f}. "
                           f"Deadlines: Apr 15, Jun 15, Sep 15, Jan 15.",
            deadline="Next quarterly deadline varies by date",
        ))
    
    return alerts


# ============================================================
# Comprehensive Analysis
# ============================================================

def analyze_red_flags(
    total_income: Decimal,
    total_tax_liability: Decimal,
    total_withheld: Decimal,
    long_term_gains: Decimal = Decimal("0"),
    short_term_gains: Decimal = Decimal("0"),
    rsu_income: Decimal = Decimal("0"),
    iso_bargain_element: Decimal = Decimal("0"),
    filing_status: str = "single",
    state: str = "CA",
    prior_year_tax: Optional[Decimal] = None,
) -> RedFlagReport:
    """
    Run comprehensive red flag analysis.
    
    Args:
        total_income: Total gross income
        total_tax_liability: Estimated total tax
        total_withheld: Total tax withheld
        long_term_gains: Long-term capital gains
        short_term_gains: Short-term capital gains
        rsu_income: RSU vesting income
        iso_bargain_element: ISO bargain element (for AMT)
        filing_status: Filing status
        state: State code
        prior_year_tax: Prior year tax (for safe harbor)
        
    Returns:
        RedFlagReport with all alerts
    """
    report = RedFlagReport()
    
    # Underwithholding checks
    report.alerts.extend(check_underwithholding(
        total_tax_liability,
        total_withheld,
        prior_year_tax,
    ))
    
    # RSU withholding check
    if rsu_income > 0:
        # Estimate actual marginal rate
        effective_rate = Decimal("0.35")  # Simplified
        if total_income > Decimal("500000"):
            effective_rate = Decimal("0.45")
        
        # Estimate RSU withholding (simplified)
        rsu_withheld = rsu_income * Decimal("0.40")
        
        report.alerts.extend(check_rsu_underwithholding(
            rsu_income,
            rsu_withheld,
            effective_rate,
            state,
        ))
    
    # AMT checks
    if iso_bargain_element > 0:
        regular_taxable = total_income - Decimal("15000")  # Simplified deduction
        report.alerts.extend(check_amt_trigger(
            regular_taxable,
            iso_bargain_element,
            filing_status,
        ))
    
    # State-specific checks
    if state == "WA":
        report.alerts.extend(check_washington_capital_gains(long_term_gains))
    
    # NIIT check
    investment_income = long_term_gains + short_term_gains
    report.alerts.extend(check_niit_threshold(
        total_income,
        investment_income,
        filing_status,
    ))
    
    # Estimated payments
    balance_due = total_tax_liability - total_withheld
    if balance_due > 0:
        report.alerts.extend(check_estimated_payments_required(
            balance_due,
            {
                "capital_gains": long_term_gains + short_term_gains,
                "rsu": rsu_income,
            },
        ))
    
    # Generate summary
    if report.has_critical:
        report.summary = f"⚠️ {len(report.critical_alerts)} critical issue(s) require immediate attention."
    elif report.warning_alerts:
        report.summary = f"⚡ {len(report.warning_alerts)} warning(s) to review."
    else:
        report.summary = "✅ No significant tax issues detected."
    
    return report
