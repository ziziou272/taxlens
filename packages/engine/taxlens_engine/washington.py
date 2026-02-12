"""
Washington state tax calculations for TaxLens.

Includes:
- No state income tax ($0 always)
- Capital gains tax: 7% on long-term gains exceeding $270,000 (2025 threshold)
- Exemption categories (real estate, retirement, small business, livestock, timber)

Based on 2025 tax rules (WA SB 5096, upheld March 2023).
"""

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


# Washington capital gains tax parameters (2025)
WA_CG_RATE = Decimal("0.07")  # 7%
WA_CG_THRESHOLD_2025 = Decimal("270000")  # $270,000


class WaCapitalGainsExemption(str, Enum):
    """Categories exempt from Washington capital gains tax."""
    REAL_ESTATE = "real_estate"
    RETIREMENT = "retirement"
    SMALL_BUSINESS = "small_business"
    LIVESTOCK = "livestock"
    TIMBER = "timber"
    AUTO_DEALERSHIP_GOODWILL = "auto_dealership_goodwill"


# Convenience aliases
REAL_ESTATE = WaCapitalGainsExemption.REAL_ESTATE
RETIREMENT = WaCapitalGainsExemption.RETIREMENT
SMALL_BUSINESS = WaCapitalGainsExemption.SMALL_BUSINESS
LIVESTOCK = WaCapitalGainsExemption.LIVESTOCK
TIMBER = WaCapitalGainsExemption.TIMBER
AUTO_DEALERSHIP_GOODWILL = WaCapitalGainsExemption.AUTO_DEALERSHIP_GOODWILL


def calculate_wa_income_tax(
    taxable_income: Decimal = Decimal("0"),
    filing_status: str = "single",
) -> Decimal:
    """
    Calculate Washington state income tax.

    Washington has no state income tax. Always returns $0.

    Args:
        taxable_income: Any income amount (ignored)
        filing_status: Filing status (ignored)

    Returns:
        Decimal("0") always
    """
    return Decimal("0")


def calculate_wa_capital_gains_tax(
    long_term_gains: Decimal,
    exemptions: Optional[list[tuple[WaCapitalGainsExemption, Decimal]]] = None,
    filing_status: str = "single",
    threshold: Decimal = WA_CG_THRESHOLD_2025,
) -> Decimal:
    """
    Calculate Washington capital gains tax (7% on LTCG over $270K).

    Only applies to long-term capital gains. Short-term gains are not subject
    to WA capital gains tax (they are taxed as ordinary income federally).

    The threshold is per return, not per person (same for MFJ).

    Args:
        long_term_gains: Total long-term capital gains before exemptions
        exemptions: List of (exemption_type, amount) tuples for exempt gains
        filing_status: Filing status (threshold is same for all statuses)
        threshold: Exemption threshold (default $270,000 for 2025)

    Returns:
        Washington capital gains tax owed
    """
    if long_term_gains <= 0:
        return Decimal("0")

    # Subtract exempt gains
    taxable_gains = long_term_gains
    if exemptions:
        total_exempt = sum(amount for _, amount in exemptions)
        taxable_gains = max(Decimal("0"), taxable_gains - total_exempt)

    # Apply threshold
    excess = max(Decimal("0"), taxable_gains - threshold)

    if excess <= 0:
        return Decimal("0")

    tax = excess * WA_CG_RATE
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
