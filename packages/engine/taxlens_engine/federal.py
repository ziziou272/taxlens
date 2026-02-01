"""
Federal tax calculations for TaxLens.

All calculations use Decimal for exact arithmetic.
Based on 2025 tax rules.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

from taxlens_engine.models import (
    FilingStatus,
    TaxYear,
    FEDERAL_BRACKETS_2025,
    LTCG_BRACKETS_2025,
)


def calculate_federal_tax(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Calculate federal income tax on ordinary income using 2025 brackets.
    
    Args:
        taxable_income: Taxable income after deductions
        filing_status: IRS filing status
        
    Returns:
        Federal tax liability (rounded to cents)
    """
    if taxable_income <= 0:
        return Decimal("0")
    
    brackets = FEDERAL_BRACKETS_2025[filing_status]
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


def calculate_ltcg_tax(
    long_term_gains: Decimal,
    taxable_ordinary_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Calculate tax on long-term capital gains using preferential rates.
    
    LTCG is "stacked" on top of ordinary income to determine the rate.
    
    Args:
        long_term_gains: Long-term capital gains + qualified dividends
        taxable_ordinary_income: Ordinary taxable income (for stacking)
        filing_status: IRS filing status
        
    Returns:
        Tax on long-term capital gains
    """
    if long_term_gains <= 0:
        return Decimal("0")
    
    brackets = LTCG_BRACKETS_2025.get(filing_status, LTCG_BRACKETS_2025[FilingStatus.SINGLE])
    tax = Decimal("0")
    
    # Starting point is where ordinary income ends
    current_position = taxable_ordinary_income
    remaining_gains = long_term_gains
    
    for threshold, rate in brackets:
        if remaining_gains <= 0:
            break
        
        if current_position >= threshold:
            # Already past this bracket
            continue
        
        # How much room in this bracket?
        room_in_bracket = threshold - current_position
        gains_in_bracket = min(remaining_gains, room_in_bracket)
        
        tax += gains_in_bracket * rate
        current_position += gains_in_bracket
        remaining_gains -= gains_in_bracket
    
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_amt(
    regular_taxable_income: Decimal,
    iso_bargain_element: Decimal,
    filing_status: FilingStatus,
    tax_year: TaxYear | None = None,
) -> Tuple[Decimal, Decimal, Decimal]:
    """
    Calculate Alternative Minimum Tax (AMT).
    
    AMT is primarily triggered by ISO exercises where the bargain element
    (FMV - strike price) is added to AMT income but not regular income.
    
    Args:
        regular_taxable_income: Regular taxable income
        iso_bargain_element: ISO bargain element (FMV - strike at exercise)
        filing_status: IRS filing status
        tax_year: Tax year config (defaults to 2025)
        
    Returns:
        Tuple of (amt_income, tentative_minimum_tax, amt_owed)
    """
    if tax_year is None:
        tax_year = TaxYear()
    
    # AMT income adds back ISO bargain element
    amt_income = regular_taxable_income + iso_bargain_element
    
    # Get exemption for filing status
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        exemption = tax_year.amt_exemption_married_jointly
        phaseout_start = tax_year.amt_phaseout_start_married
    else:
        exemption = tax_year.amt_exemption_single
        phaseout_start = tax_year.amt_phaseout_start_single
    
    # Phaseout: exemption reduced by 25% of AMT income over threshold
    if amt_income > phaseout_start:
        excess = amt_income - phaseout_start
        exemption_reduction = excess * Decimal("0.25")
        exemption = max(Decimal("0"), exemption - exemption_reduction)
    
    # AMT taxable income
    amt_taxable = max(Decimal("0"), amt_income - exemption)
    
    # AMT tax: 26% up to threshold, 28% above
    if amt_taxable <= tax_year.amt_rate_threshold:
        tmt = amt_taxable * tax_year.amt_rate_low
    else:
        tmt = (
            tax_year.amt_rate_threshold * tax_year.amt_rate_low +
            (amt_taxable - tax_year.amt_rate_threshold) * tax_year.amt_rate_high
        )
    
    tmt = tmt.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # AMT owed is the excess over regular tax (calculated separately)
    # For now, return the TMT; the caller will compare to regular tax
    return (
        amt_income.quantize(Decimal("0.01")),
        tmt,
        Decimal("0"),  # Placeholder; caller must compare to regular tax
    )


def get_marginal_rate(
    taxable_income: Decimal,
    filing_status: FilingStatus,
) -> Decimal:
    """
    Get the marginal tax rate for the given income level.
    
    Args:
        taxable_income: Taxable income after deductions
        filing_status: IRS filing status
        
    Returns:
        Marginal rate as a decimal (e.g., 0.32 for 32%)
    """
    if taxable_income <= 0:
        return Decimal("0.10")  # Lowest bracket
    
    brackets = FEDERAL_BRACKETS_2025[filing_status]
    
    for threshold, rate in brackets:
        if taxable_income <= threshold:
            return rate
    
    return brackets[-1][1]  # Top bracket


def calculate_fica(
    w2_wages: Decimal,
    filing_status: FilingStatus,
    tax_year: TaxYear | None = None,
) -> Tuple[Decimal, Decimal, Decimal]:
    """
    Calculate Social Security and Medicare taxes (employee portion).
    
    Args:
        w2_wages: W-2 wages subject to FICA
        filing_status: IRS filing status
        tax_year: Tax year config (defaults to 2025)
        
    Returns:
        Tuple of (social_security_tax, medicare_tax, additional_medicare_tax)
    """
    if tax_year is None:
        tax_year = TaxYear()
    
    # Social Security: 6.2% up to wage base
    ss_wages = min(w2_wages, tax_year.social_security_wage_base)
    ss_tax = ss_wages * tax_year.social_security_rate
    
    # Medicare: 1.45% on all wages
    medicare_tax = w2_wages * tax_year.medicare_rate
    
    # Additional Medicare: 0.9% on wages over threshold
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        threshold = tax_year.additional_medicare_threshold_married
    else:
        threshold = tax_year.additional_medicare_threshold_single
    
    if w2_wages > threshold:
        additional_medicare = (w2_wages - threshold) * tax_year.additional_medicare_rate
    else:
        additional_medicare = Decimal("0")
    
    return (
        ss_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        medicare_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        additional_medicare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )


def calculate_niit(
    investment_income: Decimal,
    magi: Decimal,
    filing_status: FilingStatus,
    tax_year: TaxYear | None = None,
) -> Decimal:
    """
    Calculate Net Investment Income Tax (NIIT).
    
    NIIT is 3.8% on the lesser of:
    - Net investment income, or
    - MAGI over threshold
    
    Args:
        investment_income: Net investment income (gains, dividends, interest)
        magi: Modified Adjusted Gross Income
        filing_status: IRS filing status
        tax_year: Tax year config (defaults to 2025)
        
    Returns:
        NIIT liability
    """
    if tax_year is None:
        tax_year = TaxYear()
    
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        threshold = tax_year.niit_threshold_married
    else:
        threshold = tax_year.niit_threshold_single
    
    if magi <= threshold:
        return Decimal("0")
    
    excess_magi = magi - threshold
    niit_base = min(investment_income, excess_magi)
    niit = niit_base * tax_year.niit_rate
    
    return niit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
