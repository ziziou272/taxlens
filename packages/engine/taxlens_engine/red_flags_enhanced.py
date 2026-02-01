"""
Enhanced Red Flags / Warning System for TaxLens.

Additional red flags beyond the base system:
- Estimated tax payment deadlines and tracking
- Quarterly underwithholding projections
- State nexus and residency warnings
- Wash sale 30-day window detection
- AMT credit carryforward tracking
"""

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date, timedelta
from enum import Enum
from typing import Optional

from .red_flags import TaxAlert, AlertSeverity, AlertCategory, RedFlagReport


# ============================================================
# Estimated Tax Payment Deadlines
# ============================================================

@dataclass
class EstimatedPaymentDeadline:
    """Estimated tax payment deadline."""
    quarter: int
    due_date: date
    period_start: date
    period_end: date
    
    @staticmethod
    def get_deadlines(year: int) -> list["EstimatedPaymentDeadline"]:
        """Get all estimated payment deadlines for a tax year."""
        return [
            EstimatedPaymentDeadline(
                quarter=1,
                due_date=date(year, 4, 15),
                period_start=date(year, 1, 1),
                period_end=date(year, 3, 31),
            ),
            EstimatedPaymentDeadline(
                quarter=2,
                due_date=date(year, 6, 15),
                period_start=date(year, 4, 1),
                period_end=date(year, 5, 31),
            ),
            EstimatedPaymentDeadline(
                quarter=3,
                due_date=date(year, 9, 15),
                period_start=date(year, 6, 1),
                period_end=date(year, 8, 31),
            ),
            EstimatedPaymentDeadline(
                quarter=4,
                due_date=date(year + 1, 1, 15),
                period_start=date(year, 9, 1),
                period_end=date(year, 12, 31),
            ),
        ]


def check_estimated_payment_deadlines(
    current_date: date,
    estimated_payments_made: dict[int, Decimal],  # quarter -> amount
    projected_annual_tax: Decimal,
    prior_year_tax: Optional[Decimal] = None,
) -> list[TaxAlert]:
    """
    Check for upcoming estimated payment deadlines and required amounts.
    
    Args:
        current_date: Current date
        estimated_payments_made: Payments already made by quarter
        projected_annual_tax: Projected total tax liability
        prior_year_tax: Prior year tax (for safe harbor)
        
    Returns:
        List of deadline-related alerts
    """
    alerts = []
    year = current_date.year
    deadlines = EstimatedPaymentDeadline.get_deadlines(year)
    
    # Calculate required quarterly payment
    # Safe harbor: pay at least 100% of prior year (110% if AGI > $150K)
    # Or 90% of current year
    if prior_year_tax and prior_year_tax > 0:
        safe_harbor_annual = prior_year_tax
    else:
        safe_harbor_annual = projected_annual_tax * Decimal("0.9")
    
    required_quarterly = (safe_harbor_annual / 4).quantize(Decimal("0.01"))
    
    total_paid = sum(estimated_payments_made.values())
    
    for deadline in deadlines:
        # Skip past deadlines (except for warning about missed ones)
        if deadline.due_date < current_date:
            # Check if this quarter was missed
            quarter_paid = estimated_payments_made.get(deadline.quarter, Decimal("0"))
            if quarter_paid < required_quarterly:
                shortfall = required_quarterly - quarter_paid
                alerts.append(TaxAlert(
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.ESTIMATED_PAYMENTS,
                    title=f"Q{deadline.quarter} Estimated Payment May Be Short",
                    message=f"Q{deadline.quarter} payment of ${quarter_paid:,.2f} may be below "
                            f"safe harbor amount of ${required_quarterly:,.2f}. "
                            f"Shortfall: ${shortfall:,.2f}",
                    amount=shortfall,
                ))
            continue
        
        # Calculate days until deadline
        days_until = (deadline.due_date - current_date).days
        
        # Check if approaching deadline
        if days_until <= 30:
            quarter_paid = estimated_payments_made.get(deadline.quarter, Decimal("0"))
            
            if quarter_paid < required_quarterly:
                severity = AlertSeverity.CRITICAL if days_until <= 7 else AlertSeverity.WARNING
                shortfall = required_quarterly - quarter_paid
                
                alerts.append(TaxAlert(
                    severity=severity,
                    category=AlertCategory.ESTIMATED_PAYMENTS,
                    title=f"Q{deadline.quarter} Estimated Payment Due {deadline.due_date.strftime('%b %d')}",
                    message=f"Estimated payment of ${required_quarterly:,.2f} due in {days_until} days. "
                            f"Already paid: ${quarter_paid:,.2f}. "
                            f"Remaining: ${shortfall:,.2f}",
                    amount=shortfall,
                    deadline=deadline.due_date.isoformat(),
                    action_required=f"Pay ${shortfall:,.2f} by {deadline.due_date.strftime('%B %d, %Y')} "
                                   f"to avoid underpayment penalty.",
                ))
            else:
                # Good news - already paid
                alerts.append(TaxAlert(
                    severity=AlertSeverity.INFO,
                    category=AlertCategory.ESTIMATED_PAYMENTS,
                    title=f"Q{deadline.quarter} Estimated Payment On Track",
                    message=f"Q{deadline.quarter} payment of ${quarter_paid:,.2f} meets or exceeds "
                            f"safe harbor requirement of ${required_quarterly:,.2f}.",
                ))
    
    return alerts


# ============================================================
# Quarterly Underwithholding Check
# ============================================================

def check_quarterly_underwithholding(
    current_date: date,
    ytd_income: Decimal,
    ytd_withheld: Decimal,
    projected_annual_income: Decimal,
    projected_annual_tax: Decimal,
    filing_status: str = "single",
) -> list[TaxAlert]:
    """
    Check if year-to-date withholding is on pace with income.
    
    Args:
        current_date: Current date
        ytd_income: Year-to-date gross income
        ytd_withheld: Year-to-date tax withheld
        projected_annual_income: Projected annual income
        projected_annual_tax: Projected annual tax
        filing_status: Filing status
        
    Returns:
        List of underwithholding alerts
    """
    alerts = []
    
    year = current_date.year
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    
    # Calculate progress through year
    days_elapsed = (current_date - year_start).days + 1
    total_days = (year_end - year_start).days + 1
    year_progress = Decimal(str(days_elapsed)) / Decimal(str(total_days))
    
    # Expected withholding at this point
    expected_ytd_tax = projected_annual_tax * year_progress
    
    # Calculate shortfall
    shortfall = expected_ytd_tax - ytd_withheld
    
    if shortfall > Decimal("1000"):
        # Calculate projected year-end shortfall
        if year_progress > 0:
            projected_rate = ytd_withheld / year_progress
            projected_year_end_withheld = projected_rate
        else:
            projected_year_end_withheld = Decimal("0")
        
        projected_shortfall = projected_annual_tax - projected_year_end_withheld
        
        severity = AlertSeverity.CRITICAL if shortfall > Decimal("5000") else AlertSeverity.WARNING
        
        alerts.append(TaxAlert(
            severity=severity,
            category=AlertCategory.WITHHOLDING,
            title="Year-to-Date Underwithholding Detected",
            message=f"As of {current_date.strftime('%B %d')}, withholding is ${shortfall:,.2f} behind pace. "
                    f"YTD withheld: ${ytd_withheld:,.2f}. "
                    f"Expected at this point: ${expected_ytd_tax:,.2f}. "
                    f"Projected year-end shortfall: ${projected_shortfall:,.2f}",
            amount=shortfall,
            action_required="Increase W-4 withholding or make estimated tax payment.",
        ))
    
    # Check if income is accelerating (common with equity comp)
    if ytd_income > 0 and projected_annual_income > 0:
        income_pace = ytd_income / (projected_annual_income * year_progress)
        if income_pace > Decimal("1.2"):  # Income 20%+ ahead of pace
            alerts.append(TaxAlert(
                severity=AlertSeverity.INFO,
                category=AlertCategory.PLANNING,
                title="Income Ahead of Projections",
                message=f"YTD income is {(income_pace - 1) * 100:.0f}% ahead of pace. "
                        f"This may be due to equity compensation or bonuses. "
                        f"Consider reviewing withholding levels.",
                action_required="Review projected annual income and adjust estimated payments if needed.",
            ))
    
    return alerts


# ============================================================
# State Nexus Warnings
# ============================================================

class StateNexusType(str, Enum):
    """Types of state tax nexus."""
    RESIDENCY = "residency"           # Full year resident
    PART_YEAR = "part_year"           # Moved during year
    WORK_DAYS = "work_days"           # Worked in state
    PROPERTY = "property"             # Own property
    BUSINESS = "business"             # Business presence


@dataclass
class StatePresence:
    """Record of presence in a state."""
    state_code: str
    days_present: int = 0
    days_worked: int = 0
    income_earned: Decimal = Decimal("0")
    has_property: bool = False
    is_primary_residence: bool = False


# State residency thresholds (days)
STATE_RESIDENCY_THRESHOLDS = {
    "CA": 9 * 30,   # 9 months = automatic presumption
    "NY": 183,      # 183 days statutory resident
    "FL": 183,
    "TX": 183,
    "WA": 183,
    # Add more states as needed
}

# States with no income tax
NO_INCOME_TAX_STATES = {"WA", "TX", "FL", "NV", "WY", "SD", "AK", "TN", "NH"}


def check_state_nexus(
    primary_state: str,
    other_state_presence: list[StatePresence],
    total_income: Decimal,
) -> list[TaxAlert]:
    """
    Check for potential state tax nexus issues.
    
    Args:
        primary_state: Primary state of residence
        other_state_presence: Presence in other states
        total_income: Total annual income
        
    Returns:
        List of state nexus alerts
    """
    alerts = []
    
    for presence in other_state_presence:
        state = presence.state_code
        
        # Skip if same as primary state
        if state == primary_state:
            continue
        
        # Skip no-income-tax states (for income tax purposes)
        if state in NO_INCOME_TAX_STATES:
            if presence.days_present > 183:
                alerts.append(TaxAlert(
                    severity=AlertSeverity.INFO,
                    category=AlertCategory.STATE_TAX,
                    title=f"Potential {state} Residency Status",
                    message=f"You spent {presence.days_present} days in {state}. "
                            f"While {state} has no income tax, extended presence may "
                            f"affect other tax obligations or residency status.",
                ))
            continue
        
        threshold = STATE_RESIDENCY_THRESHOLDS.get(state, 183)
        
        # Check if approaching or exceeding residency threshold
        if presence.days_present >= threshold:
            alerts.append(TaxAlert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.STATE_TAX,
                title=f"Potential {state} Tax Residency Triggered",
                message=f"You spent {presence.days_present} days in {state}, "
                        f"which exceeds the {threshold}-day residency threshold. "
                        f"You may be considered a statutory resident and owe {state} income tax.",
                action_required=f"Consult a tax advisor about {state} filing requirements. "
                               f"You may need to file a {state} resident or part-year return.",
            ))
        elif presence.days_present >= threshold - 30:
            # Approaching threshold
            remaining_days = threshold - presence.days_present
            alerts.append(TaxAlert(
                severity=AlertSeverity.WARNING,
                category=AlertCategory.STATE_TAX,
                title=f"Approaching {state} Residency Threshold",
                message=f"You've spent {presence.days_present} days in {state}. "
                        f"Only {remaining_days} days remaining before reaching "
                        f"the {threshold}-day statutory residency threshold.",
                action_required=f"Limit additional days in {state} to avoid residency filing requirement.",
            ))
        
        # Check for work-day taxation
        if presence.days_worked > 0 and presence.income_earned > Decimal("0"):
            # Many states tax income earned for work performed in the state
            alerts.append(TaxAlert(
                severity=AlertSeverity.WARNING,
                category=AlertCategory.STATE_TAX,
                title=f"{state} Non-Resident Income Tax May Apply",
                message=f"You worked {presence.days_worked} days in {state} "
                        f"and earned ${presence.income_earned:,.2f}. "
                        f"Non-resident income tax may apply to income earned in {state}.",
                amount=presence.income_earned,
                action_required=f"You may need to file a {state} non-resident tax return "
                               f"and potentially receive a credit on your {primary_state} return.",
            ))
    
    # Check for moving scenarios
    for presence in other_state_presence:
        if presence.is_primary_residence and presence.state_code != primary_state:
            alerts.append(TaxAlert(
                severity=AlertSeverity.WARNING,
                category=AlertCategory.STATE_TAX,
                title="Multiple Primary Residences Detected",
                message=f"Both {primary_state} and {presence.state_code} flagged as primary residence. "
                        f"This may indicate a mid-year move requiring part-year resident returns.",
                action_required="File part-year resident returns for both states if you moved during the year.",
            ))
    
    return alerts


# ============================================================
# Wash Sale Detection
# ============================================================

@dataclass
class StockTransaction:
    """Record of a stock buy or sell transaction."""
    date: date
    symbol: str
    action: str  # "buy" or "sell"
    shares: Decimal
    price: Decimal
    total: Decimal = Decimal("0")
    
    def __post_init__(self):
        if self.total == 0:
            self.total = self.shares * self.price


@dataclass
class WashSaleViolation:
    """A detected wash sale violation."""
    sell_date: date
    buy_date: date
    symbol: str
    shares_affected: Decimal
    disallowed_loss: Decimal
    days_apart: int


def detect_wash_sales(
    transactions: list[StockTransaction],
    window_days: int = 30,
) -> list[TaxAlert]:
    """
    Detect potential wash sale violations.
    
    A wash sale occurs when you sell a security at a loss and buy
    a substantially identical security within 30 days before or after.
    
    Args:
        transactions: List of stock transactions
        window_days: Wash sale window (default 30 days)
        
    Returns:
        List of wash sale alerts
    """
    alerts = []
    violations: list[WashSaleViolation] = []
    
    # Sort transactions by date
    sorted_txns = sorted(transactions, key=lambda t: t.date)
    
    # Find all sells at a loss
    sells_at_loss = []
    for i, txn in enumerate(sorted_txns):
        if txn.action == "sell":
            # Find the most recent buy to estimate cost basis
            # This is simplified - real implementation would use FIFO/specific ID
            for j in range(i - 1, -1, -1):
                prev = sorted_txns[j]
                if prev.action == "buy" and prev.symbol == txn.symbol:
                    if txn.price < prev.price:
                        loss = (prev.price - txn.price) * txn.shares
                        sells_at_loss.append((txn, loss, prev.price))
                    break
    
    # Check for wash sales
    for sell_txn, loss, cost_basis in sells_at_loss:
        window_start = sell_txn.date - timedelta(days=window_days)
        window_end = sell_txn.date + timedelta(days=window_days)
        
        # Look for buys in the wash sale window
        for txn in sorted_txns:
            if txn.action != "buy" or txn.symbol != sell_txn.symbol:
                continue
            
            if window_start <= txn.date <= window_end and txn.date != sell_txn.date:
                days_apart = abs((txn.date - sell_txn.date).days)
                
                # Calculate shares affected (minimum of sell and buy)
                shares_affected = min(sell_txn.shares, txn.shares)
                disallowed_loss = (cost_basis - sell_txn.price) * shares_affected
                
                violations.append(WashSaleViolation(
                    sell_date=sell_txn.date,
                    buy_date=txn.date,
                    symbol=sell_txn.symbol,
                    shares_affected=shares_affected,
                    disallowed_loss=disallowed_loss,
                    days_apart=days_apart,
                ))
    
    # Generate alerts for violations
    for v in violations:
        when = "before" if v.buy_date < v.sell_date else "after"
        alerts.append(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.PENALTY_RISK,
            title=f"Wash Sale Detected: {v.symbol}",
            message=f"Sold {v.symbol} at a loss on {v.sell_date.strftime('%m/%d/%Y')}, "
                    f"then bought {when} on {v.buy_date.strftime('%m/%d/%Y')} "
                    f"({v.days_apart} days apart). "
                    f"{v.shares_affected:.2f} shares affected. "
                    f"Loss of ${v.disallowed_loss:,.2f} may be disallowed.",
            amount=v.disallowed_loss,
            action_required="The disallowed loss is added to cost basis of replacement shares. "
                           "Ensure this is properly reported on Form 8949.",
        ))
    
    # Check for upcoming potential wash sales (planning mode)
    # Find recent sells at a loss and warn about buying back
    today = date.today()
    for sell_txn, loss, cost_basis in sells_at_loss:
        days_since_sell = (today - sell_txn.date).days
        if 0 <= days_since_sell <= window_days:
            days_remaining = window_days - days_since_sell
            alerts.append(TaxAlert(
                severity=AlertSeverity.INFO,
                category=AlertCategory.PLANNING,
                title=f"Wash Sale Window: {sell_txn.symbol}",
                message=f"Sold {sell_txn.symbol} at a loss {days_since_sell} days ago. "
                        f"To avoid wash sale, wait {days_remaining} more days before buying back.",
                action_required=f"Do not buy {sell_txn.symbol} until "
                               f"{(sell_txn.date + timedelta(days=window_days + 1)).strftime('%m/%d/%Y')}.",
            ))
    
    return alerts


# ============================================================
# Alert Priority System
# ============================================================

class AlertPriority(str, Enum):
    """Priority levels for alert sorting."""
    IMMEDIATE = "immediate"      # Action needed today
    THIS_WEEK = "this_week"      # Action needed within 7 days
    THIS_MONTH = "this_month"    # Action needed within 30 days
    PLANNING = "planning"        # For future planning


def calculate_alert_priority(alert: TaxAlert, current_date: date) -> AlertPriority:
    """
    Calculate priority of an alert based on severity and deadline.
    
    Args:
        alert: The tax alert
        current_date: Current date
        
    Returns:
        Alert priority
    """
    # Critical alerts are always immediate
    if alert.severity == AlertSeverity.CRITICAL:
        return AlertPriority.IMMEDIATE
    
    # Check deadline
    if alert.deadline:
        try:
            deadline_date = date.fromisoformat(alert.deadline)
            days_until = (deadline_date - current_date).days
            
            if days_until <= 0:
                return AlertPriority.IMMEDIATE
            elif days_until <= 7:
                return AlertPriority.THIS_WEEK
            elif days_until <= 30:
                return AlertPriority.THIS_MONTH
        except (ValueError, TypeError):
            pass
    
    # Warning alerts with amounts > $5000 are higher priority
    if alert.severity == AlertSeverity.WARNING and alert.amount:
        if alert.amount > Decimal("5000"):
            return AlertPriority.THIS_WEEK
        elif alert.amount > Decimal("1000"):
            return AlertPriority.THIS_MONTH
    
    return AlertPriority.PLANNING


def prioritize_alerts(alerts: list[TaxAlert], current_date: date) -> list[tuple[AlertPriority, TaxAlert]]:
    """
    Sort alerts by priority.
    
    Args:
        alerts: List of alerts
        current_date: Current date
        
    Returns:
        List of (priority, alert) tuples, sorted by priority
    """
    priority_order = {
        AlertPriority.IMMEDIATE: 0,
        AlertPriority.THIS_WEEK: 1,
        AlertPriority.THIS_MONTH: 2,
        AlertPriority.PLANNING: 3,
    }
    
    prioritized = [
        (calculate_alert_priority(a, current_date), a)
        for a in alerts
    ]
    
    return sorted(prioritized, key=lambda x: (priority_order[x[0]], x[1].severity.value))


# ============================================================
# Enhanced Comprehensive Analysis
# ============================================================

def analyze_red_flags_enhanced(
    current_date: date,
    total_income: Decimal,
    total_tax_liability: Decimal,
    total_withheld: Decimal,
    ytd_income: Decimal,
    ytd_withheld: Decimal,
    estimated_payments_made: dict[int, Decimal],
    primary_state: str,
    other_state_presence: Optional[list[StatePresence]] = None,
    stock_transactions: Optional[list[StockTransaction]] = None,
    long_term_gains: Decimal = Decimal("0"),
    short_term_gains: Decimal = Decimal("0"),
    rsu_income: Decimal = Decimal("0"),
    iso_bargain_element: Decimal = Decimal("0"),
    filing_status: str = "single",
    prior_year_tax: Optional[Decimal] = None,
) -> RedFlagReport:
    """
    Run comprehensive enhanced red flag analysis.
    
    Includes all base checks plus:
    - Estimated payment deadline tracking
    - Quarterly underwithholding analysis
    - State nexus warnings
    - Wash sale detection
    - Alert prioritization
    
    Args:
        current_date: Current date for deadline calculations
        total_income: Projected total annual income
        total_tax_liability: Projected total annual tax
        total_withheld: Total tax withheld so far
        ytd_income: Year-to-date income
        ytd_withheld: Year-to-date withholding
        estimated_payments_made: Dict of quarter -> amount paid
        primary_state: Primary state of residence
        other_state_presence: Presence in other states
        stock_transactions: Stock transactions for wash sale detection
        long_term_gains: Long-term capital gains
        short_term_gains: Short-term capital gains
        rsu_income: RSU vesting income
        iso_bargain_element: ISO bargain element for AMT
        filing_status: Filing status
        prior_year_tax: Prior year tax for safe harbor
        
    Returns:
        RedFlagReport with all alerts and priority sorting
    """
    from .red_flags import analyze_red_flags
    
    # Start with base analysis
    report = analyze_red_flags(
        total_income=total_income,
        total_tax_liability=total_tax_liability,
        total_withheld=total_withheld + sum(estimated_payments_made.values()),
        long_term_gains=long_term_gains,
        short_term_gains=short_term_gains,
        rsu_income=rsu_income,
        iso_bargain_element=iso_bargain_element,
        filing_status=filing_status,
        state=primary_state,
        prior_year_tax=prior_year_tax,
    )
    
    # Add estimated payment deadline checks
    report.alerts.extend(check_estimated_payment_deadlines(
        current_date=current_date,
        estimated_payments_made=estimated_payments_made,
        projected_annual_tax=total_tax_liability,
        prior_year_tax=prior_year_tax,
    ))
    
    # Add quarterly underwithholding check
    report.alerts.extend(check_quarterly_underwithholding(
        current_date=current_date,
        ytd_income=ytd_income,
        ytd_withheld=ytd_withheld + sum(estimated_payments_made.values()),
        projected_annual_income=total_income,
        projected_annual_tax=total_tax_liability,
        filing_status=filing_status,
    ))
    
    # Add state nexus checks
    if other_state_presence:
        report.alerts.extend(check_state_nexus(
            primary_state=primary_state,
            other_state_presence=other_state_presence,
            total_income=total_income,
        ))
    
    # Add wash sale detection
    if stock_transactions:
        report.alerts.extend(detect_wash_sales(stock_transactions))
    
    # Update summary with priority info
    prioritized = prioritize_alerts(report.alerts, current_date)
    immediate = [p for p, _ in prioritized if p == AlertPriority.IMMEDIATE]
    this_week = [p for p, _ in prioritized if p == AlertPriority.THIS_WEEK]
    
    if immediate:
        report.summary = f"🚨 {len(immediate)} IMMEDIATE action(s) required! " + report.summary
    elif this_week:
        report.summary = f"⚡ {len(this_week)} action(s) needed this week. " + report.summary
    
    return report
