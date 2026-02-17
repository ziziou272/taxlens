"""
California state tax calculations for TaxLens.

Includes:
- CA income tax brackets (1% to 12.3%)
- Mental Health Services Tax (additional 1% over $1M)
- State Disability Insurance (SDI)
- CA standard deductions

Based on 2025 tax rules.
"""

from decimal import Decimal, ROUND_HALF_UP

from taxlens_engine.models import FilingStatus


# California tax brackets for 2025
# Source: California Franchise Tax Board
# Format: (upper_limit, rate)
CA_BRACKETS_2025 = {
    FilingStatus.SINGLE: [
        (Decimal("10756"), Decimal("0.01")),
        (Decimal("25499"), Decimal("0.02")),
        (Decimal("40245"), Decimal("0.04")),
        (Decimal("55866"), Decimal("0.06")),
        (Decimal("70606"), Decimal("0.08")),
        (Decimal("360659"), Decimal("0.093")),
        (Decimal("432787"), Decimal("0.103")),
        (Decimal("721314"), Decimal("0.113")),
        (Decimal("1000000"), Decimal("0.123")),
        (Decimal("Infinity"), Decimal("0.133")),  # Includes Mental Health Tax
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (Decimal("21512"), Decimal("0.01")),
        (Decimal("50998"), Decimal("0.02")),
        (Decimal("80490"), Decimal("0.04")),
        (Decimal("111732"), Decimal("0.06")),
        (Decimal("141212"), Decimal("0.08")),
        (Decimal("721318"), Decimal("0.093")),
        (Decimal("865574"), Decimal("0.103")),
        (Decimal("1000000"), Decimal("0.113")),
        (Decimal("1442628"), Decimal("0.123")),
        (Decimal("Infinity"), Decimal("0.133")),  # Includes Mental Health Tax
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (Decimal("10756"), Decimal("0.01")),
        (Decimal("25499"), Decimal("0.02")),
        (Decimal("40245"), Decimal("0.04")),
        (Decimal("55866"), Decimal("0.06")),
        (Decimal("70606"), Decimal("0.08")),
        (Decimal("360659"), Decimal("0.093")),
        (Decimal("432787"), Decimal("0.103")),
        (Decimal("500000"), Decimal("0.113")),
        (Decimal("721314"), Decimal("0.123")),
        (Decimal("Infinity"), Decimal("0.133")),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (Decimal("21513"), Decimal("0.01")),
        (Decimal("50999"), Decimal("0.02")),
        (Decimal("65744"), Decimal("0.04")),
        (Decimal("81365"), Decimal("0.06")),
        (Decimal("96105"), Decimal("0.08")),
        (Decimal("490158"), Decimal("0.093")),
        (Decimal("588189"), Decimal("0.103")),
        (Decimal("980316"), Decimal("0.113")),
        (Decimal("1000000"), Decimal("0.123")),
        (Decimal("Infinity"), Decimal("0.133")),
    ],
}

# California standard deductions for 2025
CA_STANDARD_DEDUCTIONS = {
    FilingStatus.SINGLE: Decimal("5540"),
    FilingStatus.MARRIED_JOINTLY: Decimal("11080"),
    FilingStatus.MARRIED_SEPARATELY: Decimal("5540"),
    FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("11080"),
}

# SDI (State Disability Insurance) for 2025
# As of January 1, 2024, California removed the SDI wage base limit.
# All wages are subject to the full 1.1% SDI rate with no cap.
# Source: CA AB 102 (2023), SB 951 (2022) — effective Jan 1, 2024.
SDI_RATE = Decimal("0.011")  # 1.1%
SDI_WAGE_LIMIT = None  # Unlimited as of 2024 (cap removed)


def get_ca_standard_deduction(filing_status: FilingStatus) -> Decimal:
    """
    Get California standard deduction for filing status.
    
    Args:
        filing_status: IRS/CA filing status
        
    Returns:
        Standard deduction amount
    """
    return CA_STANDARD_DEDUCTIONS[filing_status]


def calculate_california_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Calculate California income tax using 2025 brackets.
    
    This includes the base tax brackets but NOT the Mental Health
    Services Tax (which is calculated separately for clarity).
    
    Args:
        taxable_income: California taxable income (after CA deductions)
        filing_status: Filing status
        
    Returns:
        California income tax (excluding SDI, including Mental Health Tax)
    """
    if taxable_income <= 0:
        return Decimal("0")
    
    brackets = CA_BRACKETS_2025[filing_status]
    tax = Decimal("0")
    prev_threshold = Decimal("0")
    
    for threshold, rate in brackets:
        if taxable_income <= prev_threshold:
            break
        
        # Handle "Infinity" threshold
        if threshold == Decimal("Infinity"):
            taxable_in_bracket = taxable_income - prev_threshold
        else:
            taxable_in_bracket = min(taxable_income, threshold) - prev_threshold
        
        if taxable_in_bracket > 0:
            tax += taxable_in_bracket * rate
        
        prev_threshold = threshold
    
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_mental_health_tax(taxable_income: Decimal) -> Decimal:
    """
    Calculate Mental Health Services Tax (Proposition 63).
    
    Additional 1% tax on taxable income over $1,000,000.
    This is already included in the top bracket rate (13.3% = 12.3% + 1%),
    so this function is for informational purposes or separate display.
    
    Args:
        taxable_income: California taxable income
        
    Returns:
        Mental Health Services Tax amount
    """
    threshold = Decimal("1000000")
    if taxable_income <= threshold:
        return Decimal("0")
    
    excess = taxable_income - threshold
    tax = excess * Decimal("0.01")
    
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_sdi(wages: Decimal) -> Decimal:
    """
    Calculate California State Disability Insurance (SDI).

    As of January 1, 2024, California removed the SDI wage base limit.
    SDI is now 1.1% of ALL wages with no annual cap.
    This is withheld from employee wages.

    Args:
        wages: W-2 wages subject to SDI

    Returns:
        SDI amount
    """
    sdi = wages * SDI_RATE

    return sdi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_ca_marginal_rate(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Get California marginal tax rate for the given income level.
    
    Args:
        taxable_income: California taxable income
        filing_status: Filing status
        
    Returns:
        Marginal rate as a decimal (e.g., 0.093 for 9.3%)
    """
    if taxable_income <= 0:
        return Decimal("0.01")  # Lowest bracket
    
    brackets = CA_BRACKETS_2025[filing_status]
    
    for threshold, rate in brackets:
        if taxable_income <= threshold:
            return rate
    
    return brackets[-1][1]  # Top bracket (13.3%)


def calculate_ca_total_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
    wages_for_sdi: Decimal = Decimal("0"),
    include_sdi: bool = False,
) -> Decimal:
    """
    Calculate total California tax including optional SDI.
    
    Args:
        taxable_income: California taxable income
        filing_status: Filing status
        wages_for_sdi: W-2 wages for SDI calculation
        include_sdi: Whether to include SDI in total
        
    Returns:
        Total California tax
    """
    income_tax = calculate_california_tax(taxable_income, filing_status)
    
    if include_sdi and wages_for_sdi > 0:
        sdi = calculate_sdi(wages_for_sdi)
        return income_tax + sdi
    
    return income_tax
