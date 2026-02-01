"""
Capital Gains Tax Alert System for TaxLens.

Focuses on Washington State's capital gains tax (effective 2022):
- 7% tax on long-term capital gains over $270,000 (2025 threshold)
- Only applies to gains from stocks, bonds, etc.
- Does NOT apply to real estate, retirement accounts, etc.

Note: WA capital gains tax was upheld by WA Supreme Court in 2023.
It's classified as an "excise tax" not an income tax.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from enum import Enum


class ThresholdStatus(str, Enum):
    """Status relative to capital gains threshold."""
    BELOW = "below"  # Well below threshold
    APPROACHING = "approaching"  # Getting close
    AT_RISK = "at_risk"  # Very close or over
    EXCEEDED = "exceeded"  # Over threshold


# Washington State Capital Gains Tax Constants (2025)
WA_CG_THRESHOLD_2025 = Decimal("270000")  # Indexed for inflation
WA_CG_RATE = Decimal("0.07")  # 7%

# Thresholds for alerts (percentage of threshold)
APPROACHING_PERCENT = Decimal("0.70")  # 70%
AT_RISK_PERCENT = Decimal("0.90")  # 90%


@dataclass
class CapitalGainsAlert:
    """Capital gains tax threshold alert."""
    status: ThresholdStatus
    message: str
    
    # Current gains
    ytd_long_term_gains: Decimal
    threshold: Decimal
    
    # Remaining room
    room_remaining: Decimal
    percent_of_threshold: Decimal
    
    # If over threshold
    taxable_gains: Decimal
    estimated_wa_tax: Decimal
    
    # Upcoming transactions that would trigger
    at_risk_transactions: list[dict]
    
    @property
    def exceeds_threshold(self) -> bool:
        """Returns True if over the threshold."""
        return self.status == ThresholdStatus.EXCEEDED


def check_wa_capital_gains(
    ytd_long_term_gains: Decimal,
    planned_gains: Optional[list[dict]] = None,
    threshold: Decimal = WA_CG_THRESHOLD_2025,
    tax_rate: Decimal = WA_CG_RATE,
) -> CapitalGainsAlert:
    """
    Check WA capital gains tax exposure.
    
    Args:
        ytd_long_term_gains: Year-to-date long-term capital gains
        planned_gains: List of planned sales [{"description", "expected_gain"}]
        threshold: WA threshold (default 2025)
        tax_rate: WA rate (7%)
        
    Returns:
        CapitalGainsAlert with analysis
    """
    planned_gains = planned_gains or []
    
    # Calculate room remaining
    room_remaining = max(Decimal("0"), threshold - ytd_long_term_gains)
    
    # Calculate percentage of threshold
    if threshold > 0:
        percent = ((ytd_long_term_gains / threshold) * 100).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
    else:
        percent = Decimal("0")
    
    # Determine status
    if ytd_long_term_gains > threshold:
        status = ThresholdStatus.EXCEEDED
    elif ytd_long_term_gains >= threshold * AT_RISK_PERCENT:
        status = ThresholdStatus.AT_RISK
    elif ytd_long_term_gains >= threshold * APPROACHING_PERCENT:
        status = ThresholdStatus.APPROACHING
    else:
        status = ThresholdStatus.BELOW
    
    # Calculate taxable gains and estimated tax
    taxable_gains = max(Decimal("0"), ytd_long_term_gains - threshold)
    estimated_tax = (taxable_gains * tax_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    # Check which planned transactions would trigger/exceed threshold
    at_risk = []
    cumulative = ytd_long_term_gains
    for txn in planned_gains:
        gain = Decimal(str(txn.get("expected_gain", 0)))
        cumulative += gain
        if cumulative > threshold and cumulative - gain <= threshold:
            at_risk.append({
                "description": txn.get("description", "Unknown"),
                "gain": gain,
                "would_trigger": True,
            })
        elif cumulative > threshold:
            at_risk.append({
                "description": txn.get("description", "Unknown"),
                "gain": gain,
                "additional_tax": (gain * tax_rate).quantize(Decimal("0.01")),
            })
    
    # Generate message
    if status == ThresholdStatus.EXCEEDED:
        message = (
            f"Over WA threshold! ${taxable_gains:,.2f} taxable at 7% = "
            f"${estimated_tax:,.2f} WA tax."
        )
    elif status == ThresholdStatus.AT_RISK:
        message = (
            f"At risk! Only ${room_remaining:,.2f} remaining under threshold. "
            f"Any large sale will trigger WA tax."
        )
    elif status == ThresholdStatus.APPROACHING:
        message = (
            f"Approaching threshold ({percent}% used). "
            f"${room_remaining:,.2f} remaining before WA tax kicks in."
        )
    else:
        message = (
            f"Below threshold ({percent}% used). "
            f"${room_remaining:,.2f} of tax-free gains remaining."
        )
    
    return CapitalGainsAlert(
        status=status,
        message=message,
        ytd_long_term_gains=ytd_long_term_gains,
        threshold=threshold,
        room_remaining=room_remaining,
        percent_of_threshold=percent,
        taxable_gains=taxable_gains,
        estimated_wa_tax=estimated_tax,
        at_risk_transactions=at_risk,
    )


def optimize_capital_gains_timing(
    ytd_gains: Decimal,
    planned_sales: list[dict],
    threshold: Decimal = WA_CG_THRESHOLD_2025,
) -> dict:
    """
    Optimize timing of sales to minimize WA capital gains tax.
    
    Strategy: Stay under threshold each year if possible.
    
    Args:
        ytd_gains: Current year gains
        planned_sales: Sales to optimize [{description, gain, urgency}]
        threshold: WA threshold
        
    Returns:
        Optimization recommendation
    """
    room_this_year = max(Decimal("0"), threshold - ytd_gains)
    
    # Sort by urgency then by gain size
    sales = sorted(
        planned_sales,
        key=lambda x: (x.get("urgency", 3), -Decimal(str(x.get("gain", 0))))
    )
    
    this_year = []
    next_year = []
    this_year_total = Decimal("0")
    
    for sale in sales:
        gain = Decimal(str(sale.get("gain", 0)))
        urgency = sale.get("urgency", 3)  # 1=high, 3=low
        
        if urgency == 1:
            # Must do this year regardless
            this_year.append(sale)
            this_year_total += gain
        elif this_year_total + gain <= room_this_year:
            # Fits in this year's room
            this_year.append(sale)
            this_year_total += gain
        else:
            # Defer to next year
            next_year.append(sale)
    
    # Calculate tax implications
    total_this_year = ytd_gains + this_year_total
    if total_this_year > threshold:
        tax_this_year = ((total_this_year - threshold) * WA_CG_RATE).quantize(
            Decimal("0.01")
        )
    else:
        tax_this_year = Decimal("0")
    
    return {
        "recommendation": "Optimized sale timing",
        "this_year": {
            "sales": this_year,
            "total_gains": this_year_total,
            "estimated_wa_tax": tax_this_year,
        },
        "defer_to_next_year": {
            "sales": next_year,
            "reason": "Stay under WA threshold this year",
        },
        "notes": [
            f"Room this year: ${room_this_year:,.2f}",
            f"This year sales: ${this_year_total:,.2f}",
            f"WA tax this year: ${tax_this_year:,.2f}",
        ],
    }


def wa_capital_gains_examples():
    """Example scenarios for WA capital gains tax."""
    
    # Scenario 1: Under threshold
    under = check_wa_capital_gains(
        ytd_long_term_gains=Decimal("150000"),
    )
    
    # Scenario 2: Over threshold
    over = check_wa_capital_gains(
        ytd_long_term_gains=Decimal("400000"),
    )
    
    # Scenario 3: With planned sales
    with_planned = check_wa_capital_gains(
        ytd_long_term_gains=Decimal("200000"),
        planned_gains=[
            {"description": "AAPL sale", "expected_gain": Decimal("50000")},
            {"description": "RSU sale", "expected_gain": Decimal("80000")},
        ],
    )
    
    return {
        "under_threshold": {
            "gains": under.ytd_long_term_gains,
            "status": under.status.value,
            "message": under.message,
            "wa_tax": under.estimated_wa_tax,
        },
        "over_threshold": {
            "gains": over.ytd_long_term_gains,
            "status": over.status.value,
            "message": over.message,
            "wa_tax": over.estimated_wa_tax,
        },
        "with_planned_sales": {
            "current_gains": with_planned.ytd_long_term_gains,
            "status": with_planned.status.value,
            "at_risk": with_planned.at_risk_transactions,
        },
    }


def estimate_wa_tax_on_rsu_sale(
    shares: Decimal,
    sale_price: Decimal,
    cost_basis: Decimal,
    ytd_gains: Decimal = Decimal("0"),
    threshold: Decimal = WA_CG_THRESHOLD_2025,
) -> dict:
    """
    Estimate WA capital gains tax on RSU sale.
    
    Note: RSU sale gains are usually SHORT-term (taxed as ordinary income)
    unless held >1 year after vesting. WA tax only applies to LONG-term gains.
    
    Args:
        shares: Number of shares to sell
        sale_price: Sale price per share
        cost_basis: Cost basis per share (FMV at vesting)
        ytd_gains: Year-to-date LTCG already realized
        threshold: WA threshold
        
    Returns:
        Tax estimate
    """
    gain_per_share = sale_price - cost_basis
    total_gain = (shares * gain_per_share).quantize(Decimal("0.01"))
    
    # Check if this would trigger WA tax
    cumulative = ytd_gains + total_gain
    
    if cumulative <= threshold:
        wa_tax = Decimal("0")
        triggers_wa = False
    elif ytd_gains >= threshold:
        # Already over, full gain taxed
        wa_tax = (total_gain * WA_CG_RATE).quantize(Decimal("0.01"))
        triggers_wa = False  # Already triggered
    else:
        # This sale pushes over threshold
        taxable = cumulative - threshold
        wa_tax = (taxable * WA_CG_RATE).quantize(Decimal("0.01"))
        triggers_wa = True
    
    return {
        "shares": shares,
        "sale_price": sale_price,
        "cost_basis": cost_basis,
        "gain_per_share": gain_per_share,
        "total_gain": total_gain,
        "ytd_gains_before": ytd_gains,
        "ytd_gains_after": cumulative,
        "wa_tax": wa_tax,
        "triggers_wa_threshold": triggers_wa,
        "notes": [
            "WA tax only applies to LONG-TERM gains",
            "RSUs held <1yr from vesting = SHORT-TERM (no WA tax)",
            "Verify holding period before calculating WA tax",
        ],
    }
