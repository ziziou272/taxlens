"""
New York state tax calculations for TaxLens.

Includes:
- NY state income tax brackets (4% to 10.9%)
- NYC city income tax (3.078% to 3.876%)
- Yonkers surcharge (16.75% of state tax)
- MCTMT (Metropolitan Commuter Transportation Mobility Tax)
- NY standard deductions

Based on 2025 tax rules.
"""

from decimal import Decimal, ROUND_HALF_UP

from taxlens_engine.models import FilingStatus


# ---------------------------------------------------------------------------
# NY State Income Tax Brackets 2025
# Format: (upper_limit, rate)
# ---------------------------------------------------------------------------

NY_BRACKETS_2025 = {
    FilingStatus.SINGLE: [
        (Decimal("8500"), Decimal("0.04")),
        (Decimal("11700"), Decimal("0.045")),
        (Decimal("13900"), Decimal("0.0525")),
        (Decimal("80650"), Decimal("0.055")),
        (Decimal("215400"), Decimal("0.06")),
        (Decimal("1077550"), Decimal("0.0685")),
        (Decimal("5000000"), Decimal("0.0965")),
        (Decimal("25000000"), Decimal("0.103")),
        (Decimal("Infinity"), Decimal("0.109")),
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (Decimal("8500"), Decimal("0.04")),
        (Decimal("11700"), Decimal("0.045")),
        (Decimal("13900"), Decimal("0.0525")),
        (Decimal("80650"), Decimal("0.055")),
        (Decimal("215400"), Decimal("0.06")),
        (Decimal("1077550"), Decimal("0.0685")),
        (Decimal("5000000"), Decimal("0.0965")),
        (Decimal("25000000"), Decimal("0.103")),
        (Decimal("Infinity"), Decimal("0.109")),
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (Decimal("17150"), Decimal("0.04")),
        (Decimal("23600"), Decimal("0.045")),
        (Decimal("27900"), Decimal("0.0525")),
        (Decimal("161550"), Decimal("0.055")),
        (Decimal("323200"), Decimal("0.06")),
        (Decimal("2155350"), Decimal("0.0685")),
        (Decimal("5000000"), Decimal("0.0965")),
        (Decimal("25000000"), Decimal("0.103")),
        (Decimal("Infinity"), Decimal("0.109")),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (Decimal("12800"), Decimal("0.04")),
        (Decimal("17650"), Decimal("0.045")),
        (Decimal("20900"), Decimal("0.0525")),
        (Decimal("107650"), Decimal("0.055")),
        (Decimal("269300"), Decimal("0.06")),
        (Decimal("1616450"), Decimal("0.0685")),
        (Decimal("5000000"), Decimal("0.0965")),
        (Decimal("25000000"), Decimal("0.103")),
        (Decimal("Infinity"), Decimal("0.109")),
    ],
}

# ---------------------------------------------------------------------------
# NYC City Tax Brackets 2025
# ---------------------------------------------------------------------------

NYC_BRACKETS_2025 = {
    FilingStatus.SINGLE: [
        (Decimal("12000"), Decimal("0.03078")),
        (Decimal("25000"), Decimal("0.03762")),
        (Decimal("50000"), Decimal("0.03819")),
        (Decimal("Infinity"), Decimal("0.03876")),
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (Decimal("12000"), Decimal("0.03078")),
        (Decimal("25000"), Decimal("0.03762")),
        (Decimal("50000"), Decimal("0.03819")),
        (Decimal("Infinity"), Decimal("0.03876")),
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (Decimal("21600"), Decimal("0.03078")),
        (Decimal("45000"), Decimal("0.03762")),
        (Decimal("90000"), Decimal("0.03819")),
        (Decimal("Infinity"), Decimal("0.03876")),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (Decimal("14400"), Decimal("0.03078")),
        (Decimal("30000"), Decimal("0.03762")),
        (Decimal("60000"), Decimal("0.03819")),
        (Decimal("Infinity"), Decimal("0.03876")),
    ],
}

# ---------------------------------------------------------------------------
# NY Standard Deductions 2025
# ---------------------------------------------------------------------------

NY_STANDARD_DEDUCTIONS = {
    FilingStatus.SINGLE: Decimal("8000"),
    FilingStatus.MARRIED_JOINTLY: Decimal("16050"),
    FilingStatus.MARRIED_SEPARATELY: Decimal("8000"),
    FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("11200"),
}

# Yonkers surcharge rate
YONKERS_SURCHARGE_RATE = Decimal("0.1675")

# MCTMT rate for self-employed in MCTD
MCTMT_RATE = Decimal("0.0034")

# Supplemental withholding rate
NY_SUPPLEMENTAL_WITHHOLDING_RATE = Decimal("0.1170")


def _calculate_progressive_tax(taxable_income: Decimal, brackets: list) -> Decimal:
    """Calculate tax using progressive brackets."""
    if taxable_income <= 0:
        return Decimal("0")

    tax = Decimal("0")
    prev = Decimal("0")

    for threshold, rate in brackets:
        if taxable_income <= prev:
            break
        if threshold == Decimal("Infinity"):
            taxable_in_bracket = taxable_income - prev
        else:
            taxable_in_bracket = min(taxable_income, threshold) - prev
        if taxable_in_bracket > 0:
            tax += taxable_in_bracket * rate
        prev = threshold

    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_ny_standard_deduction(filing_status: FilingStatus) -> Decimal:
    """Get New York standard deduction for filing status."""
    return NY_STANDARD_DEDUCTIONS[filing_status]


def calculate_ny_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Calculate New York State income tax using 2025 brackets.

    Args:
        taxable_income: NY taxable income (after NY deductions)
        filing_status: Filing status

    Returns:
        NY state income tax amount
    """
    return _calculate_progressive_tax(
        taxable_income, NY_BRACKETS_2025[filing_status]
    )


def calculate_nyc_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Calculate New York City income tax using 2025 brackets.

    Args:
        taxable_income: NYC taxable income
        filing_status: Filing status

    Returns:
        NYC city income tax amount
    """
    return _calculate_progressive_tax(
        taxable_income, NYC_BRACKETS_2025[filing_status]
    )


def calculate_yonkers_surcharge(state_tax: Decimal) -> Decimal:
    """
    Calculate Yonkers resident surcharge (16.75% of NY state tax).

    Args:
        state_tax: NY state income tax amount

    Returns:
        Yonkers surcharge amount
    """
    if state_tax <= 0:
        return Decimal("0")
    surcharge = state_tax * YONKERS_SURCHARGE_RATE
    return surcharge.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_mctmt(self_employment_income: Decimal) -> Decimal:
    """
    Calculate Metropolitan Commuter Transportation Mobility Tax.

    Applies to self-employed individuals in the MCTD (Metropolitan
    Commuter Transportation District) at 0.34%.

    Args:
        self_employment_income: Self-employment income in MCTD

    Returns:
        MCTMT amount
    """
    if self_employment_income <= 0:
        return Decimal("0")
    tax = self_employment_income * MCTMT_RATE
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_ny_marginal_rate(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Get NY state marginal tax rate for the given income level.

    Args:
        taxable_income: NY taxable income
        filing_status: Filing status

    Returns:
        Marginal rate as a decimal
    """
    if taxable_income <= 0:
        return Decimal("0.04")

    brackets = NY_BRACKETS_2025[filing_status]
    for threshold, rate in brackets:
        if taxable_income <= threshold:
            return rate
    return brackets[-1][1]


def calculate_ny_rsu_sourcing(
    total_rsu_income: Decimal,
    ny_work_days: int,
    total_work_days: int,
) -> Decimal:
    """
    Calculate NY-source RSU income based on work-day allocation.

    Args:
        total_rsu_income: Total RSU income
        ny_work_days: Work days in NY during vesting period
        total_work_days: Total work days during vesting period

    Returns:
        NY-source RSU income
    """
    if total_work_days <= 0:
        return Decimal("0")
    ratio = Decimal(ny_work_days) / Decimal(total_work_days)
    return (total_rsu_income * ratio).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_ny_total_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
    is_ny_resident: bool = True,
    is_nyc_resident: bool = False,
    is_yonkers_resident: bool = False,
    self_employment_income: Decimal = Decimal("0"),
    is_mctd: bool = False,
) -> Decimal:
    """
    Calculate total New York tax including state, city, and surcharges.

    Args:
        taxable_income: NY taxable income
        filing_status: Filing status
        is_ny_resident: Whether taxpayer is a NY state resident
        is_nyc_resident: Whether taxpayer is a NYC resident
        is_yonkers_resident: Whether taxpayer is a Yonkers resident
        self_employment_income: Self-employment income (for MCTMT)
        is_mctd: Whether in Metropolitan Commuter Transportation District

    Returns:
        Total NY tax (state + city + surcharges)
    """
    if not is_ny_resident:
        # Nonresidents still owe state tax on NY-source income
        pass

    state_tax = calculate_ny_tax(taxable_income, filing_status)
    total = state_tax

    if is_nyc_resident:
        total += calculate_nyc_tax(taxable_income, filing_status)

    if is_yonkers_resident:
        total += calculate_yonkers_surcharge(state_tax)

    if is_mctd and self_employment_income > 0:
        total += calculate_mctmt(self_employment_income)

    return total
