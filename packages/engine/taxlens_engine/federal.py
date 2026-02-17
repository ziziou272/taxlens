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
    ItemizedDeductionsDetail,
    AboveTheLineDeductionsDetail,
)


# ---------------------------------------------------------------------------
# EITC Parameters for 2025
# Phase-in and phase-out rates are statutory (IRC §32); amounts match task spec.
# Phase-out thresholds for 1/2/3+ children match 2024 IRS tables (Rev. Proc. 2024-40).
# ---------------------------------------------------------------------------
_EITC_PARAMS = {
    0: {
        "max_credit": Decimal("632"),
        "phase_in_rate": Decimal("0.0765"),
        "phase_out_rate": Decimal("0.0765"),
        "phase_out_start_single": Decimal("10330"),
        "phase_out_start_mfj": Decimal("17530"),
        "phase_out_end_single": Decimal("18591"),
        "phase_out_end_mfj": Decimal("25791"),
    },
    1: {
        "max_credit": Decimal("4213"),
        "phase_in_rate": Decimal("0.34"),
        "phase_out_rate": Decimal("0.1598"),
        "phase_out_start_single": Decimal("23511"),
        "phase_out_start_mfj": Decimal("30711"),
        "phase_out_end_single": Decimal("49875"),
        "phase_out_end_mfj": Decimal("57075"),
    },
    2: {
        "max_credit": Decimal("6960"),
        "phase_in_rate": Decimal("0.40"),
        "phase_out_rate": Decimal("0.2106"),
        "phase_out_start_single": Decimal("23511"),
        "phase_out_start_mfj": Decimal("30711"),
        "phase_out_end_single": Decimal("56557"),
        "phase_out_end_mfj": Decimal("63757"),
    },
    3: {  # 3+ children
        "max_credit": Decimal("7830"),
        "phase_in_rate": Decimal("0.45"),
        "phase_out_rate": Decimal("0.2106"),
        "phase_out_start_single": Decimal("23511"),
        "phase_out_start_mfj": Decimal("30711"),
        "phase_out_end_single": Decimal("60689"),
        "phase_out_end_mfj": Decimal("67889"),
    },
}


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
    # IRC §3101(b)(2): MFJ=$250K, MFS=$125K, all others=$200K
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        threshold = tax_year.additional_medicare_threshold_married
    elif filing_status == FilingStatus.MARRIED_SEPARATELY:
        threshold = tax_year.additional_medicare_threshold_married_separately
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
    
    # NIIT thresholds: MFJ=$250K, MFS=$125K, all others=$200K (IRC §1411)
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        threshold = tax_year.niit_threshold_married
    elif filing_status == FilingStatus.MARRIED_SEPARATELY:
        threshold = tax_year.niit_threshold_married_separately
    else:
        threshold = tax_year.niit_threshold_single
    
    if magi <= threshold:
        return Decimal("0")
    
    excess_magi = magi - threshold
    niit_base = min(investment_income, excess_magi)
    niit = niit_base * tax_year.niit_rate
    
    return niit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# 1. Itemized Deductions (IRC §§163, 164, 170, 213)
# ---------------------------------------------------------------------------

def calculate_itemized_deductions(
    agi: Decimal,
    filing_status: FilingStatus,
    mortgage_interest: Decimal = Decimal("0"),
    mortgage_loan_balance: Decimal = Decimal("0"),
    salt_paid: Decimal = Decimal("0"),
    charitable: Decimal = Decimal("0"),
    medical_expenses: Decimal = Decimal("0"),
    tax_year: TaxYear | None = None,
) -> ItemizedDeductionsDetail:
    """
    Calculate itemized deductions.

    - Mortgage interest: limited if loan balance > $750K (post-2017).
      Pass ``mortgage_loan_balance`` for proportional scaling; if 0 the full
      ``mortgage_interest`` is accepted (caller already scaled).
    - SALT: capped at $10,000 ($5,000 MFS) per IRC §164(b)(6).
    - Charitable: deductible as provided (no additional cap applied here).
    - Medical: only the portion exceeding 7.5% of AGI (IRC §213).

    Args:
        agi: Adjusted Gross Income (used for medical floor).
        filing_status: IRS filing status.
        mortgage_interest: Mortgage interest actually paid.
        mortgage_loan_balance: Acquisition debt balance (for $750K limit check).
        salt_paid: State/local taxes paid (property + income or sales).
        charitable: Cash/non-cash charitable contributions.
        medical_expenses: Total qualified medical expenses paid.
        tax_year: TaxYear config (defaults to 2025).

    Returns:
        ItemizedDeductionsDetail with each component and total.
    """
    if tax_year is None:
        tax_year = TaxYear()

    # Mortgage interest — proportional cap when loan > $750K
    if mortgage_loan_balance > tax_year.mortgage_loan_limit:
        ratio = tax_year.mortgage_loan_limit / mortgage_loan_balance
        deductible_mortgage = (mortgage_interest * ratio).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        deductible_mortgage = mortgage_interest

    # SALT cap
    if filing_status == FilingStatus.MARRIED_SEPARATELY:
        salt_cap = tax_year.salt_cap_mfs
    else:
        salt_cap = tax_year.salt_cap_general
    deductible_salt = min(salt_paid, salt_cap)

    # Charitable contributions (no further cap for cash ≤ 60% AGI applied here)
    deductible_charitable = max(Decimal("0"), charitable)

    # Medical: amount exceeding 7.5% of AGI
    medical_floor = (agi * tax_year.medical_expense_floor_pct).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    deductible_medical = max(Decimal("0"), medical_expenses - medical_floor)

    total = (
        deductible_mortgage
        + deductible_salt
        + deductible_charitable
        + deductible_medical
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return ItemizedDeductionsDetail(
        mortgage_interest=deductible_mortgage.quantize(Decimal("0.01")),
        salt=deductible_salt.quantize(Decimal("0.01")),
        salt_paid=salt_paid.quantize(Decimal("0.01")),
        charitable=deductible_charitable.quantize(Decimal("0.01")),
        medical=deductible_medical.quantize(Decimal("0.01")),
        medical_paid=medical_expenses.quantize(Decimal("0.01")),
        total=total,
    )


# ---------------------------------------------------------------------------
# 2. Above-the-Line Deductions (AGI Adjustments)
# ---------------------------------------------------------------------------

def calculate_above_the_line_deductions(
    gross_income: Decimal,
    filing_status: FilingStatus,
    contributions_401k: Decimal = Decimal("0"),
    ira_contributions: Decimal = Decimal("0"),
    hsa_contributions: Decimal = Decimal("0"),
    student_loan_interest: Decimal = Decimal("0"),
    age_over_50: bool = False,
    hsa_family_coverage: bool = False,
    tax_year: TaxYear | None = None,
) -> AboveTheLineDeductionsDetail:
    """
    Calculate above-the-line deductions that reduce gross income to AGI.

    - 401(k): capped at $23,500 ($31,000 with catch-up for 50+).
    - Traditional IRA: capped at $7,000 ($8,000 with catch-up for 50+).
      (Deductibility phase-out for active participants not applied here.)
    - HSA: capped at $4,300 (single) or $8,550 (family).
    - Student loan interest: capped at $2,500; phases out based on MAGI.
      MAGI for this purpose approximated as gross_income (ignores the
      deduction itself to avoid circularity; conservative approach).

    Args:
        gross_income: Total gross income (before any deductions).
        filing_status: IRS filing status.
        contributions_401k: Employee pre-tax 401(k) contributions.
        ira_contributions: Traditional IRA contributions.
        hsa_contributions: HSA contributions.
        student_loan_interest: Student loan interest paid.
        age_over_50: True if taxpayer (or older spouse for MFJ) is ≥50.
        hsa_family_coverage: True if enrolled in family HDHP; else single.
        tax_year: TaxYear config (defaults to 2025).

    Returns:
        AboveTheLineDeductionsDetail with each component and total.
    """
    if tax_year is None:
        tax_year = TaxYear()

    # 401(k) — IRC §402(g)
    limit_401k = tax_year.limit_401k
    if age_over_50:
        limit_401k += tax_year.limit_401k_catchup
    deductible_401k = min(contributions_401k, limit_401k)

    # IRA — IRC §219
    limit_ira = tax_year.limit_ira
    if age_over_50:
        limit_ira += tax_year.limit_ira_catchup
    deductible_ira = min(ira_contributions, limit_ira)

    # HSA — IRC §223
    if hsa_family_coverage or filing_status == FilingStatus.MARRIED_JOINTLY:
        hsa_limit = tax_year.limit_hsa_family
    else:
        hsa_limit = tax_year.limit_hsa_single
    deductible_hsa = min(hsa_contributions, hsa_limit)

    # Student loan interest — IRC §221; phase-out based on MAGI
    # Use gross_income as MAGI approximation (conservative)
    magi = gross_income
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        po_start = tax_year.student_loan_phaseout_start_mfj
        po_end = tax_year.student_loan_phaseout_end_mfj
    else:
        po_start = tax_year.student_loan_phaseout_start_single
        po_end = tax_year.student_loan_phaseout_end_single

    raw_student_loan = min(student_loan_interest, tax_year.limit_student_loan_interest)
    if magi <= po_start:
        deductible_sli = raw_student_loan
    elif magi >= po_end:
        deductible_sli = Decimal("0")
    else:
        phase_out_fraction = (magi - po_start) / (po_end - po_start)
        deductible_sli = (raw_student_loan * (Decimal("1") - phase_out_fraction)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    total = (
        deductible_401k + deductible_ira + deductible_hsa + deductible_sli
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return AboveTheLineDeductionsDetail(
        contributions_401k=deductible_401k.quantize(Decimal("0.01")),
        ira_contributions=deductible_ira.quantize(Decimal("0.01")),
        hsa_contributions=deductible_hsa.quantize(Decimal("0.01")),
        student_loan_interest=deductible_sli,
        total=total,
    )


# ---------------------------------------------------------------------------
# 3. Child Tax Credit / Dependent Credits (IRC §24)
# ---------------------------------------------------------------------------

def calculate_child_tax_credit(
    magi: Decimal,
    filing_status: FilingStatus,
    num_children_under_17: int,
    num_other_dependents: int = 0,
    federal_tax_before_credits: Decimal = Decimal("0"),
    tax_year: TaxYear | None = None,
) -> Tuple[Decimal, Decimal, Decimal]:
    """
    Calculate Child Tax Credit (CTC), Other Dependent Credit, and
    Additional Child Tax Credit (ACTC).

    CTC is non-refundable (reduces tax to 0); ACTC is refundable.

    Phase-out: $50 reduction per $1,000 (or fraction) of MAGI over threshold.
        - Single/HOH: $200,000
        - MFJ: $400,000

    Args:
        magi: Modified Adjusted Gross Income (≈ AGI for most taxpayers).
        filing_status: IRS filing status.
        num_children_under_17: Number of qualifying children under 17.
        num_other_dependents: Dependents who don't qualify for CTC.
        federal_tax_before_credits: Federal income tax before credits
            (used to cap non-refundable CTC).
        tax_year: TaxYear config (defaults to 2025).

    Returns:
        Tuple of (child_tax_credit, other_dependent_credit, actc)
        where child_tax_credit and other_dependent_credit are non-refundable
        and actc is the refundable additional child tax credit.
    """
    if tax_year is None:
        tax_year = TaxYear()

    if num_children_under_17 <= 0 and num_other_dependents <= 0:
        return Decimal("0"), Decimal("0"), Decimal("0")

    # Phase-out threshold
    if filing_status == FilingStatus.MARRIED_JOINTLY:
        po_threshold = tax_year.ctc_phaseout_start_mfj
    else:
        po_threshold = tax_year.ctc_phaseout_start_single

    # Full CTC before phase-out
    gross_ctc = Decimal(str(num_children_under_17)) * tax_year.ctc_per_child

    # Phase-out: $50 per $1,000 (or fraction) over threshold
    if magi > po_threshold:
        excess = magi - po_threshold
        # Round UP to nearest $1,000 (IRC §24(b)(1))
        increments = ((excess + Decimal("999")) // Decimal("1000"))
        reduction = increments * tax_year.ctc_phaseout_rate
        gross_ctc = max(Decimal("0"), gross_ctc - reduction)

    # Other dependent credit (not subject to same phase-out for simplicity)
    odc = Decimal(str(num_other_dependents)) * tax_year.other_dependent_credit_amount

    # Non-refundable portion of CTC: can't exceed tax liability
    non_refundable_ctc = min(gross_ctc, max(Decimal("0"), federal_tax_before_credits - odc))
    non_refundable_ctc = max(Decimal("0"), non_refundable_ctc)

    # ODC is non-refundable (limited to remaining tax after CTC)
    remaining_tax_after_ctc = max(Decimal("0"), federal_tax_before_credits - non_refundable_ctc)
    applied_odc = min(odc, remaining_tax_after_ctc)

    # ACTC (refundable): up to $1,700/child for the unused CTC
    unused_ctc = gross_ctc - non_refundable_ctc
    actc = min(
        unused_ctc,
        Decimal(str(num_children_under_17)) * tax_year.ctc_refundable_per_child,
    )
    actc = max(Decimal("0"), actc)

    return (
        non_refundable_ctc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        applied_odc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        actc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )


# ---------------------------------------------------------------------------
# 4. Earned Income Credit (EITC) — IRC §32
# ---------------------------------------------------------------------------

def calculate_eitc(
    earned_income: Decimal,
    agi: Decimal,
    filing_status: FilingStatus,
    num_children: int,
    investment_income: Decimal = Decimal("0"),
    tax_year: TaxYear | None = None,
) -> Decimal:
    """
    Calculate the Earned Income Tax Credit (EITC) for 2025.

    EITC is fully refundable.  Investment income limit: $11,600.
    MFS filers are ineligible (IRC §32(d)).

    Phase-in/phase-out uses the GREATER of earned income or AGI for
    the phase-out determination (IRS standard).

    Args:
        earned_income: Earned income (wages, self-employment).
        agi: Adjusted Gross Income.
        filing_status: IRS filing status.
        num_children: Number of qualifying children (capped at 3 for rate table).
        investment_income: Net investment income (disqualifies if > $11,600).
        tax_year: TaxYear config (defaults to 2025).

    Returns:
        EITC amount (refundable credit).
    """
    if tax_year is None:
        tax_year = TaxYear()

    # MFS is ineligible
    if filing_status == FilingStatus.MARRIED_SEPARATELY:
        return Decimal("0")

    # Investment income disqualifier
    if investment_income > tax_year.eitc_investment_income_limit:
        return Decimal("0")

    # Must have positive earned income
    if earned_income <= Decimal("0"):
        return Decimal("0")

    # Clamp children lookup to max 3
    key = min(num_children, 3)
    params = _EITC_PARAMS[key]

    # Phase-in: credit = earned_income × phase_in_rate, capped at max_credit
    tentative_credit = min(
        earned_income * params["phase_in_rate"],
        params["max_credit"],
    )

    # Phase-out: use greater of earned income or AGI
    phase_out_base = max(earned_income, agi)
    is_mfj = filing_status == FilingStatus.MARRIED_JOINTLY
    po_start = params["phase_out_start_mfj"] if is_mfj else params["phase_out_start_single"]
    po_end = params["phase_out_end_mfj"] if is_mfj else params["phase_out_end_single"]

    if phase_out_base <= po_start:
        credit = tentative_credit
    elif phase_out_base >= po_end:
        credit = Decimal("0")
    else:
        reduction = (phase_out_base - po_start) * params["phase_out_rate"]
        credit = max(Decimal("0"), tentative_credit - reduction)

    return credit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# 5. Education Credits (IRC §25A)
# ---------------------------------------------------------------------------

def _education_phase_out_fraction(
    magi: Decimal,
    po_start: Decimal,
    po_end: Decimal,
) -> Decimal:
    """Return the phase-out reduction fraction (0.0 = no reduction, 1.0 = full)."""
    if magi <= po_start:
        return Decimal("0")
    if magi >= po_end:
        return Decimal("1")
    return (magi - po_start) / (po_end - po_start)


def calculate_education_credits(
    magi: Decimal,
    filing_status: FilingStatus,
    education_expenses: Decimal = Decimal("0"),
    education_type: str = "aotc",
    num_students: int = 1,
    tax_year: TaxYear | None = None,
) -> Tuple[Decimal, Decimal]:
    """
    Calculate American Opportunity Tax Credit (AOTC) or Lifetime Learning
    Credit (LLC).

    AOTC:
        - Up to $2,500/student; 40% refundable (max $1,000 refundable/student).
        - First $2,000 of expenses at 100%, next $2,000 at 25%.
        - Phase-out: $80K–$90K single, $160K–$180K MFJ.
    LLC:
        - Up to $2,000/return (20% of first $10,000 of expenses); non-refundable.
        - Phase-out: $80K–$90K single, $160K–$180K MFJ.

    MFS filers are ineligible for both credits.

    Args:
        magi: Modified Adjusted Gross Income.
        filing_status: IRS filing status.
        education_expenses: Qualified education expenses paid.
        education_type: "aotc" or "llc".
        num_students: Number of eligible students (AOTC only; LLC is per-return).
        tax_year: TaxYear config (defaults to 2025).

    Returns:
        Tuple of (non_refundable_credit, refundable_credit).
        LLC always returns refundable=0.
    """
    if tax_year is None:
        tax_year = TaxYear()

    # MFS ineligible
    if filing_status == FilingStatus.MARRIED_SEPARATELY:
        return Decimal("0"), Decimal("0")

    is_mfj = filing_status == FilingStatus.MARRIED_JOINTLY

    if education_type.lower() == "llc":
        po_start = tax_year.llc_phaseout_start_mfj if is_mfj else tax_year.llc_phaseout_start_single
        po_end = tax_year.llc_phaseout_end_mfj if is_mfj else tax_year.llc_phaseout_end_single
        po_fraction = _education_phase_out_fraction(magi, po_start, po_end)

        # LLC: 20% of first $10,000 of expenses → max $2,000
        raw_credit = min(education_expenses, Decimal("10000")) * Decimal("0.20")
        raw_credit = min(raw_credit, tax_year.llc_max_credit)
        credit = (raw_credit * (Decimal("1") - po_fraction)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return credit, Decimal("0")

    # AOTC
    po_start = tax_year.aotc_phaseout_start_mfj if is_mfj else tax_year.aotc_phaseout_start_single
    po_end = tax_year.aotc_phaseout_end_mfj if is_mfj else tax_year.aotc_phaseout_end_single
    po_fraction = _education_phase_out_fraction(magi, po_start, po_end)

    # AOTC per student: 100% of first $2,000 + 25% of next $2,000 = max $2,500
    per_student_expenses = education_expenses / Decimal(str(max(num_students, 1)))
    first_2k = min(per_student_expenses, Decimal("2000"))
    next_2k = max(Decimal("0"), min(per_student_expenses - Decimal("2000"), Decimal("2000")))
    per_student_credit = first_2k * Decimal("1") + next_2k * Decimal("0.25")
    per_student_credit = min(per_student_credit, tax_year.aotc_max_credit)

    total_raw_credit = per_student_credit * Decimal(str(num_students))

    # Apply phase-out
    total_credit_after_po = (total_raw_credit * (Decimal("1") - po_fraction)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Split: 60% non-refundable, 40% refundable (max $1,000/student refundable)
    refundable = min(
        total_credit_after_po * tax_year.aotc_refundable_pct,
        tax_year.aotc_refundable_max * Decimal(str(num_students)),
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    non_refundable = (total_credit_after_po - refundable).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return non_refundable, refundable
