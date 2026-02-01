"""
Alternative Minimum Tax (AMT) warning system.

ISO exercises are a major AMT trigger for tech employees.
The bargain element (FMV - strike price) on ISO exercises
is added to AMT income, potentially causing a surprise tax bill.

This module helps predict AMT exposure before exercising ISOs.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class AMTRiskLevel(str, Enum):
    """AMT risk level."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AMTAlert:
    """
    Alert for potential AMT liability from ISO exercises.
    """
    risk_level: AMTRiskLevel
    iso_bargain_element: Decimal
    regular_tax: Decimal
    estimated_amt: Decimal
    amt_liability: Decimal  # Additional tax owed
    
    # Context
    filing_status: str
    exemption_amount: Decimal
    exemption_phaseout: Decimal
    
    message: str = ""
    recommendation: str = ""
    
    @property
    def triggers_amt(self) -> bool:
        return self.amt_liability > Decimal("0")


# 2024 AMT exemption amounts (indexed for inflation annually)
AMT_EXEMPTIONS = {
    "single": Decimal("85700"),
    "mfj": Decimal("133300"),  # Married filing jointly
    "mfs": Decimal("66650"),  # Married filing separately
    "hoh": Decimal("85700"),  # Head of household
}

# Phaseout thresholds (exemption reduced by 25% of AMTI over this)
AMT_PHASEOUT_THRESHOLDS = {
    "single": Decimal("609350"),
    "mfj": Decimal("1218700"),
    "mfs": Decimal("609350"),
    "hoh": Decimal("609350"),
}

# AMT rates
AMT_RATE_1 = Decimal("0.26")  # Up to threshold
AMT_RATE_2 = Decimal("0.28")  # Above threshold
AMT_RATE_THRESHOLD = {
    "single": Decimal("232600"),
    "mfj": Decimal("232600"),
    "mfs": Decimal("116300"),
    "hoh": Decimal("232600"),
}


def calculate_amt_exemption(
    amti: Decimal,
    filing_status: str = "single",
) -> Decimal:
    """
    Calculate AMT exemption amount after phaseout.
    
    The exemption phases out at 25 cents per dollar of AMTI
    over the phaseout threshold.
    
    Args:
        amti: Alternative Minimum Taxable Income
        filing_status: Filing status
        
    Returns:
        Exemption amount (may be zero if fully phased out)
    """
    base_exemption = AMT_EXEMPTIONS.get(filing_status, AMT_EXEMPTIONS["single"])
    phaseout_threshold = AMT_PHASEOUT_THRESHOLDS.get(
        filing_status, AMT_PHASEOUT_THRESHOLDS["single"]
    )
    
    if amti <= phaseout_threshold:
        return base_exemption
    
    # Phase out at 25% rate
    excess = amti - phaseout_threshold
    reduction = excess * Decimal("0.25")
    
    return max(Decimal("0"), base_exemption - reduction)


def estimate_amt_liability(
    regular_taxable_income: Decimal,
    iso_bargain_element: Decimal,
    other_amt_adjustments: Decimal = Decimal("0"),
    filing_status: str = "single",
) -> dict:
    """
    Estimate AMT liability from ISO exercises.
    
    Args:
        regular_taxable_income: Regular taxable income
        iso_bargain_element: Total (FMV - strike) from ISO exercises
        other_amt_adjustments: Other AMT preference items
        filing_status: Filing status
        
    Returns:
        Dict with AMT calculation details
    """
    # Calculate AMTI (Alternative Minimum Taxable Income)
    # Start with regular taxable income + ISO bargain element
    amti = regular_taxable_income + iso_bargain_element + other_amt_adjustments
    
    # Get exemption after phaseout
    exemption = calculate_amt_exemption(amti, filing_status)
    
    # AMT base = AMTI - exemption
    amt_base = max(Decimal("0"), amti - exemption)
    
    # Calculate tentative minimum tax
    rate_threshold = AMT_RATE_THRESHOLD.get(filing_status, AMT_RATE_THRESHOLD["single"])
    
    if amt_base <= rate_threshold:
        tentative_amt = amt_base * AMT_RATE_1
    else:
        tentative_amt = (rate_threshold * AMT_RATE_1) + (
            (amt_base - rate_threshold) * AMT_RATE_2
        )
    
    return {
        "amti": amti,
        "exemption": exemption,
        "amt_base": amt_base,
        "tentative_amt": tentative_amt,
        "rate_applied": str(AMT_RATE_1) if amt_base <= rate_threshold else f"{AMT_RATE_1}/{AMT_RATE_2}",
    }


def check_amt_trigger(
    iso_exercises: list[dict],
    regular_tax: Decimal,
    filing_status: str = "single",
    regular_taxable_income: Optional[Decimal] = None,
) -> AMTAlert:
    """
    Warn if ISO exercises will trigger AMT.
    
    Args:
        iso_exercises: List of ISO exercises with 'shares', 'strike_price', 'fmv'
        regular_tax: Calculated regular tax liability
        filing_status: Filing status (single, mfj, mfs, hoh)
        regular_taxable_income: Optional - for more accurate AMT calc
        
    Returns:
        AMTAlert with risk assessment
    """
    # Calculate total bargain element
    total_bargain = Decimal("0")
    for exercise in iso_exercises:
        shares = Decimal(str(exercise.get("shares", 0)))
        strike = Decimal(str(exercise.get("strike_price", 0)))
        fmv = Decimal(str(exercise.get("fmv", 0)))
        bargain = (fmv - strike) * shares
        total_bargain += max(Decimal("0"), bargain)
    
    # If no taxable income provided, estimate from regular tax
    # (rough approximation)
    if regular_taxable_income is None:
        # Assume ~22% effective rate to back-calculate
        regular_taxable_income = regular_tax / Decimal("0.22")
    
    # Calculate AMT
    amt_result = estimate_amt_liability(
        regular_taxable_income=regular_taxable_income,
        iso_bargain_element=total_bargain,
        filing_status=filing_status,
    )
    
    tentative_amt = amt_result["tentative_amt"]
    
    # AMT liability = max(0, tentative_amt - regular_tax)
    amt_liability = max(Decimal("0"), tentative_amt - regular_tax)
    
    # Determine risk level
    if amt_liability == 0:
        risk_level = AMTRiskLevel.LOW
        message = "ISO exercises unlikely to trigger AMT."
        recommendation = "Safe to proceed with exercises."
    elif amt_liability < Decimal("10000"):
        risk_level = AMTRiskLevel.MODERATE
        message = f"ISO exercises may trigger ~${amt_liability:,.0f} in AMT."
        recommendation = "Consider spreading exercises across tax years."
    elif amt_liability < Decimal("50000"):
        risk_level = AMTRiskLevel.HIGH
        message = f"ISO exercises will likely trigger ~${amt_liability:,.0f} in AMT."
        recommendation = "Consult tax advisor. Consider partial exercise or waiting."
    else:
        risk_level = AMTRiskLevel.CRITICAL
        message = f"Critical: ISO exercises will trigger ~${amt_liability:,.0f} in AMT!"
        recommendation = "Strongly recommend consulting CPA before exercising. Consider multi-year strategy."
    
    # Add bargain element context
    message += f" (Bargain element: ${total_bargain:,.0f})"
    
    return AMTAlert(
        risk_level=risk_level,
        iso_bargain_element=total_bargain,
        regular_tax=regular_tax,
        estimated_amt=tentative_amt,
        amt_liability=amt_liability,
        filing_status=filing_status,
        exemption_amount=amt_result["exemption"],
        exemption_phaseout=AMT_PHASEOUT_THRESHOLDS.get(filing_status, Decimal("0")),
        message=message,
        recommendation=recommendation,
    )


def optimal_iso_exercise_amount(
    regular_tax: Decimal,
    regular_taxable_income: Decimal,
    available_isos: list[dict],
    filing_status: str = "single",
    target_amt_liability: Decimal = Decimal("0"),
) -> dict:
    """
    Calculate optimal ISO exercise amount to minimize/avoid AMT.
    
    Args:
        regular_tax: Current regular tax liability
        regular_taxable_income: Current taxable income
        available_isos: Available ISOs to exercise
        filing_status: Filing status
        target_amt_liability: Target maximum AMT (0 = avoid entirely)
        
    Returns:
        Dict with recommended exercise strategy
    """
    # Simple binary search for optimal exercise amount
    # Find the point where AMT starts to exceed regular tax
    
    total_available_bargain = sum(
        Decimal(str(iso.get("shares", 0))) * 
        (Decimal(str(iso.get("fmv", 0))) - Decimal(str(iso.get("strike_price", 0))))
        for iso in available_isos
    )
    
    # Test incremental amounts
    safe_amount = Decimal("0")
    
    for pct in range(0, 101, 5):
        test_bargain = total_available_bargain * Decimal(str(pct)) / Decimal("100")
        
        amt_result = estimate_amt_liability(
            regular_taxable_income=regular_taxable_income,
            iso_bargain_element=test_bargain,
            filing_status=filing_status,
        )
        
        amt_liability = max(Decimal("0"), amt_result["tentative_amt"] - regular_tax)
        
        if amt_liability <= target_amt_liability:
            safe_amount = test_bargain
        else:
            break
    
    # Calculate shares this represents
    if total_available_bargain > 0:
        safe_pct = safe_amount / total_available_bargain
    else:
        safe_pct = Decimal("1")
    
    return {
        "max_safe_bargain_element": safe_amount,
        "total_available_bargain": total_available_bargain,
        "safe_percentage": float(safe_pct * 100),
        "recommendation": f"Exercise up to ${safe_amount:,.0f} in bargain element to stay under AMT threshold.",
        "remaining_for_next_year": total_available_bargain - safe_amount,
    }
