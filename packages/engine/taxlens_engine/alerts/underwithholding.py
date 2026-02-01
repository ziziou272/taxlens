"""
Underwithholding penalty detection.

The IRS imposes penalties for underpayment of estimated tax.
Safe harbor rules allow you to avoid penalties if you:
1. Pay 100% of prior year tax liability (110% if AGI > $150K), OR
2. Pay 90% of current year tax liability

This module checks withholding against these thresholds and
provides early warning if you're on track for penalties.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class SafeHarborStatus(str, Enum):
    """Safe harbor status for underwithholding."""
    SAFE = "safe"  # Meeting safe harbor
    WARNING = "warning"  # Close to threshold
    DANGER = "danger"  # Will likely owe penalty
    UNKNOWN = "unknown"


@dataclass
class UnderwithholdingAlert:
    """
    Alert for potential underwithholding penalty.
    """
    status: SafeHarborStatus
    ytd_withheld: Decimal
    projected_liability: Decimal
    prior_year_liability: Decimal
    
    # Thresholds
    current_year_threshold: Decimal  # 90% of current year
    prior_year_threshold: Decimal  # 100% or 110% of prior year
    
    # Shortfall amounts
    shortfall_vs_current: Optional[Decimal] = None
    shortfall_vs_prior: Optional[Decimal] = None
    
    # Recommended action
    recommended_q4_payment: Optional[Decimal] = None
    message: str = ""
    
    @property
    def is_safe(self) -> bool:
        return self.status == SafeHarborStatus.SAFE


def check_underwithholding(
    ytd_withheld: Decimal,
    projected_liability: Decimal,
    prior_year_liability: Decimal,
    prior_year_agi: Optional[Decimal] = None,
    is_q4: bool = True,
) -> UnderwithholdingAlert:
    """
    Check if underwithholding will trigger penalties.
    
    Safe harbor rules:
    - 100% of prior year tax liability, OR
    - 90% of current year tax liability
    - If prior year AGI > $150K (MFJ) / $75K (single): 110% of prior year
    
    Args:
        ytd_withheld: Total withholding paid year-to-date
        projected_liability: Estimated total tax liability for current year
        prior_year_liability: Actual tax liability from prior year
        prior_year_agi: Prior year AGI (for 110% rule)
        is_q4: Whether we're in Q4 (affects recommendations)
        
    Returns:
        UnderwithholdingAlert with status and recommendations
    """
    # Determine prior year threshold (100% or 110%)
    high_income_threshold = Decimal("150000")  # Simplified; varies by filing status
    
    prior_year_pct = Decimal("1.00")  # 100%
    if prior_year_agi and prior_year_agi > high_income_threshold:
        prior_year_pct = Decimal("1.10")  # 110% for high earners
    
    current_year_threshold = projected_liability * Decimal("0.90")
    prior_year_threshold = prior_year_liability * prior_year_pct
    
    # Calculate shortfalls
    shortfall_vs_current = max(Decimal("0"), current_year_threshold - ytd_withheld)
    shortfall_vs_prior = max(Decimal("0"), prior_year_threshold - ytd_withheld)
    
    # Check safe harbor - need to meet EITHER threshold
    meets_current_year = ytd_withheld >= current_year_threshold
    meets_prior_year = ytd_withheld >= prior_year_threshold
    
    if meets_current_year or meets_prior_year:
        status = SafeHarborStatus.SAFE
        message = "You're within safe harbor - no penalty expected."
    else:
        # How close are we?
        min_shortfall = min(shortfall_vs_current, shortfall_vs_prior)
        pct_of_liability = ytd_withheld / max(projected_liability, Decimal("1"))
        
        if pct_of_liability >= Decimal("0.80"):
            status = SafeHarborStatus.WARNING
            message = f"Warning: Withholding is below safe harbor by ${min_shortfall:,.0f}. Consider an estimated payment."
        else:
            status = SafeHarborStatus.DANGER
            message = f"Alert: Significant underwithholding detected. You're short by ${min_shortfall:,.0f}. Immediate action recommended."
    
    # Calculate recommended Q4 payment
    recommended_payment = None
    if status != SafeHarborStatus.SAFE:
        # Pay enough to meet the lower threshold
        min_needed = min(current_year_threshold, prior_year_threshold)
        recommended_payment = max(Decimal("0"), min_needed - ytd_withheld)
        
        if is_q4 and recommended_payment > Decimal("0"):
            message += f" Recommended Q4 estimated payment: ${recommended_payment:,.0f}"
    
    return UnderwithholdingAlert(
        status=status,
        ytd_withheld=ytd_withheld,
        projected_liability=projected_liability,
        prior_year_liability=prior_year_liability,
        current_year_threshold=current_year_threshold,
        prior_year_threshold=prior_year_threshold,
        shortfall_vs_current=shortfall_vs_current,
        shortfall_vs_prior=shortfall_vs_prior,
        recommended_q4_payment=recommended_payment,
        message=message,
    )


def calculate_underpayment_penalty(
    underpayment: Decimal,
    days_late: int,
    annual_rate: Decimal = Decimal("0.08"),  # IRS rate varies
) -> Decimal:
    """
    Estimate underpayment penalty.
    
    The IRS charges interest on underpayments, calculated daily.
    Rate is federal short-term rate + 3%.
    
    Args:
        underpayment: Amount underpaid
        days_late: Number of days the payment was late
        annual_rate: Annual interest rate (default 8%)
        
    Returns:
        Estimated penalty amount
    """
    if underpayment <= 0 or days_late <= 0:
        return Decimal("0")
    
    daily_rate = annual_rate / Decimal("365")
    penalty = underpayment * daily_rate * days_late
    
    return penalty.quantize(Decimal("0.01"))


def quarterly_payment_schedule(
    total_liability: Decimal,
    q1_paid: Decimal = Decimal("0"),
    q2_paid: Decimal = Decimal("0"),
    q3_paid: Decimal = Decimal("0"),
) -> dict:
    """
    Calculate recommended quarterly payment schedule.
    
    Safe harbor requires payments roughly quarterly:
    - Q1: Due April 15 (25% of annual)
    - Q2: Due June 15 (25% of annual)
    - Q3: Due September 15 (25% of annual)
    - Q4: Due January 15 (25% of annual)
    
    Args:
        total_liability: Expected annual tax liability
        q1_paid: Amount already paid in Q1
        q2_paid: Amount already paid in Q2
        q3_paid: Amount already paid in Q3
        
    Returns:
        Dict with payment schedule and recommendations
    """
    quarterly_amount = total_liability / Decimal("4")
    
    q1_shortfall = max(Decimal("0"), quarterly_amount - q1_paid)
    q2_shortfall = max(Decimal("0"), quarterly_amount - q2_paid)
    q3_shortfall = max(Decimal("0"), quarterly_amount - q3_paid)
    
    total_paid = q1_paid + q2_paid + q3_paid
    remaining = max(Decimal("0"), total_liability - total_paid)
    
    # Q4 needs to cover remaining + any prior shortfalls to avoid penalty
    total_shortfall = q1_shortfall + q2_shortfall + q3_shortfall
    
    return {
        "quarterly_target": quarterly_amount,
        "q1": {"paid": q1_paid, "target": quarterly_amount, "shortfall": q1_shortfall},
        "q2": {"paid": q2_paid, "target": quarterly_amount, "shortfall": q2_shortfall},
        "q3": {"paid": q3_paid, "target": quarterly_amount, "shortfall": q3_shortfall},
        "q4": {
            "remaining_liability": remaining,
            "recommended_payment": remaining,
            "catch_up_amount": total_shortfall,
        },
        "total_paid": total_paid,
        "total_liability": total_liability,
    }
