# Task 2: Federal Tax Calculation Engine - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document provides the complete specification for calculating federal income tax for high-income individuals. All figures are for **Tax Year 2025** (filed in 2026), reflecting the One Big Beautiful Bill Act (OBBBA) changes signed July 4, 2025.

---

## 1. 2025 Federal Income Tax Brackets

### 1.1 Tax Rates by Filing Status

| Tax Rate | Single | Married Filing Jointly | Married Filing Separately | Head of Household |
|----------|--------|----------------------|--------------------------|-------------------|
| **10%** | $0 – $11,925 | $0 – $23,850 | $0 – $11,925 | $0 – $17,000 |
| **12%** | $11,926 – $48,475 | $23,851 – $96,950 | $11,926 – $48,475 | $17,001 – $64,850 |
| **22%** | $48,476 – $103,350 | $96,951 – $206,700 | $48,476 – $103,350 | $64,851 – $103,350 |
| **24%** | $103,351 – $197,300 | $206,701 – $394,600 | $103,351 – $197,300 | $103,351 – $197,300 |
| **32%** | $197,301 – $250,525 | $394,601 – $501,050 | $197,301 – $250,525 | $197,301 – $250,500 |
| **35%** | $250,526 – $626,350 | $501,051 – $751,600 | $250,526 – $375,800 | $250,501 – $626,350 |
| **37%** | $626,351+ | $751,601+ | $375,801+ | $626,351+ |

*Source: IRS Revenue Procedure 2024-40, updated by OBBBA*

### 1.2 Tax Calculation Formula (Pseudocode)

```python
def calculate_federal_tax(taxable_income: float, filing_status: str) -> float:
    """
    Calculate federal income tax using progressive brackets.
    """
    brackets = get_brackets(filing_status)  # Returns list of (threshold, rate) tuples

    tax = 0.0
    previous_threshold = 0

    for threshold, rate in brackets:
        if taxable_income <= threshold:
            tax += (taxable_income - previous_threshold) * rate
            break
        else:
            tax += (threshold - previous_threshold) * rate
            previous_threshold = threshold

    return tax

# Example: Single filer, $200,000 taxable income
# Tax = $11,925 * 0.10 + ($48,475 - $11,925) * 0.12 + ($103,350 - $48,475) * 0.22
#     + ($197,300 - $103,350) * 0.24 + ($200,000 - $197,300) * 0.32
# Tax = $1,192.50 + $4,386 + $12,072.50 + $22,548 + $864 = $41,063
```

### 1.3 Pre-computed Tax Tables

For efficiency, store the cumulative tax at each bracket boundary:

| Filing Status | Bracket Start | Cumulative Tax at Start |
|---------------|---------------|------------------------|
| **Single** | $0 | $0 |
| | $11,925 | $1,192.50 |
| | $48,475 | $5,578.50 |
| | $103,350 | $17,651.00 |
| | $197,300 | $40,199.00 |
| | $250,525 | $57,231.00 |
| | $626,350 | $188,769.75 |
| **MFJ** | $0 | $0 |
| | $23,850 | $2,385.00 |
| | $96,950 | $11,157.00 |
| | $206,700 | $35,302.00 |
| | $394,600 | $80,398.00 |
| | $501,050 | $114,462.00 |
| | $751,600 | $202,154.50 |

---

## 2. Standard Deduction (2025)

### 2.1 Base Standard Deduction

| Filing Status | Amount |
|---------------|--------|
| Single | $15,750 |
| Married Filing Jointly | $31,500 |
| Married Filing Separately | $15,750 |
| Head of Household | $23,625 |
| Qualifying Surviving Spouse | $31,500 |

*Note: OBBBA increased these from original IRS amounts ($15,000 single, $30,000 MFJ)*

### 2.2 Additional Standard Deduction (Age 65+ or Blind)

| Filing Status | Additional Amount |
|---------------|-------------------|
| Single | $2,000 per qualifying condition |
| Head of Household | $2,000 per qualifying condition |
| Married (either status) | $1,600 per qualifying person per condition |

**Example:** 65+ and blind single filer: $15,750 + $2,000 + $2,000 = $19,750

### 2.3 NEW: Senior Bonus Deduction (OBBBA)

For taxpayers age 65+ with MAGI below threshold:

| Filing Status | Max Bonus | Phase-out Start | Phase-out End |
|---------------|-----------|-----------------|---------------|
| Single | $6,000 | $75,000 | $175,000 |
| MFJ (both 65+) | $12,000 | $150,000 | $250,000 |

Phase-out rate: 6% for every dollar over threshold

---

## 3. Itemized Deductions

### 3.1 SALT Cap (State and Local Tax)

| Year | Cap | Notes |
|------|-----|-------|
| 2025 | $40,000 (MFJ) / $20,000 (Single/MFS) | OBBBA increased from $10,000 |
| 2026 | $40,400 (MFJ) / $20,200 (Single) | Indexed for inflation |

**Phase-out for high earners (OBBBA):**
- Income limit: $500,000 (MFJ) / $250,000 (Single)
- Phase-out threshold: $505,000 (MFJ) / $252,500 (Single) for 2026
- Increases 1% annually through 2029
- After 2029: Permanently reduced to $10,000 ($5,000 MFS)

### 3.2 Mortgage Interest Deduction

| Loan Type | Limit |
|-----------|-------|
| Acquisition debt (post-12/15/2017) | Interest on first $750,000 |
| Acquisition debt (pre-12/15/2017) | Interest on first $1,000,000 |
| Home equity debt | NOT deductible (unless used for home improvement) |

### 3.3 Charitable Contributions

| Type | AGI Limit |
|------|-----------|
| Cash to public charities | 60% of AGI |
| Property to public charities | 30% of AGI |
| Cash to private foundations | 30% of AGI |

### 3.4 Itemized Deduction Limitation (OBBBA - High Earners)

For taxpayers in the **37% bracket**:
- Itemized deductions limited to **35 cents on the dollar**
- This is a new limitation added by OBBBA

---

## 4. Alternative Minimum Tax (AMT)

### 4.1 AMT Exemption Amounts (2025)

| Filing Status | Exemption |
|---------------|-----------|
| Single | $88,100 |
| Married Filing Jointly | $137,000 |
| Married Filing Separately | $68,500 |
| Head of Household | $88,100 |

### 4.2 AMT Exemption Phase-out (2025)

| Filing Status | Phase-out Threshold | Phase-out Rate |
|---------------|---------------------|----------------|
| Single | $626,350 | 25% |
| Married Filing Jointly | $1,252,700 | 25% |
| Married Filing Separately | $626,350 | 25% |

**Phase-out formula:**
```
exemption_reduction = (AMTI - threshold) * 0.25
actual_exemption = max(0, exemption - exemption_reduction)
```

**Exemption fully phased out at:**
- Single: $626,350 + ($88,100 / 0.25) = $978,750
- MFJ: $1,252,700 + ($137,000 / 0.25) = $1,800,700

### 4.3 AMT Tax Rates

| AMTI (after exemption) | Rate |
|------------------------|------|
| Up to $239,100 (MFJ) / $119,550 (others) | 26% |
| Above threshold | 28% |

### 4.4 AMT Calculation Formula

```python
def calculate_amt(regular_taxable_income: float,
                  amt_adjustments: float,
                  filing_status: str) -> float:
    """
    Calculate Alternative Minimum Tax.
    """
    # Step 1: Calculate AMTI
    amti = regular_taxable_income + amt_adjustments

    # Step 2: Apply exemption with phase-out
    exemption = get_amt_exemption(filing_status)
    threshold = get_amt_phaseout_threshold(filing_status)

    if amti > threshold:
        reduction = (amti - threshold) * 0.25
        exemption = max(0, exemption - reduction)

    # Step 3: Calculate tentative minimum tax
    amt_taxable = max(0, amti - exemption)

    bracket_threshold = get_amt_bracket_threshold(filing_status)
    if amt_taxable <= bracket_threshold:
        tentative_mt = amt_taxable * 0.26
    else:
        tentative_mt = (bracket_threshold * 0.26) + ((amt_taxable - bracket_threshold) * 0.28)

    # Step 4: AMT is excess over regular tax
    regular_tax = calculate_federal_tax(regular_taxable_income, filing_status)
    amt = max(0, tentative_mt - regular_tax)

    return amt
```

### 4.5 Common AMT Preference Items

| Item | Treatment |
|------|-----------|
| State and local taxes | Add back to income |
| Property taxes | Add back to income |
| Standard deduction | Not allowed for AMT |
| ISO exercise (bargain element) | Add to AMT income |
| Private activity bond interest | Add to AMT income |
| Miscellaneous itemized deductions | Add back |

### 4.6 2026 AMT Changes (OBBBA)

| Change | 2025 | 2026+ |
|--------|------|-------|
| Phase-out threshold (MFJ) | $1,252,700 | $1,000,000 (indexed) |
| Phase-out threshold (Single) | $626,350 | $500,000 (indexed) |
| Phase-out rate | 25% | **50%** |

**Impact:** More taxpayers will face AMT in 2026+

---

## 5. Net Investment Income Tax (NIIT)

### 5.1 NIIT Thresholds

| Filing Status | MAGI Threshold |
|---------------|----------------|
| Single | $200,000 |
| Head of Household | $200,000 |
| Married Filing Jointly | $250,000 |
| Married Filing Separately | $125,000 |
| Qualifying Widow(er) | $250,000 |

*Note: These thresholds are NOT indexed for inflation*

### 5.2 NIIT Rate

**3.8%** on the lesser of:
1. Net Investment Income (NII)
2. MAGI exceeding the threshold

### 5.3 What Counts as Net Investment Income

**Included:**
- Interest income
- Dividends (ordinary and qualified)
- Capital gains (short-term and long-term)
- Rental and royalty income
- Passive business income
- Annuity distributions (taxable portion)

**Excluded:**
- Wages and self-employment income
- Active business income (S-corp, partnership where materially participating)
- Retirement plan distributions (IRA, 401k)
- Social Security benefits
- Alimony
- Tax-exempt interest
- Gain excluded under home sale exclusion ($250K/$500K)

### 5.4 NIIT Calculation Formula

```python
def calculate_niit(magi: float, nii: float, filing_status: str) -> float:
    """
    Calculate Net Investment Income Tax.
    """
    threshold = get_niit_threshold(filing_status)

    if magi <= threshold:
        return 0.0

    excess_magi = magi - threshold
    taxable_amount = min(nii, excess_magi)

    return taxable_amount * 0.038
```

**Example:**
- Single filer, MAGI = $280,000, NII = $50,000
- Excess MAGI = $280,000 - $200,000 = $80,000
- NIIT base = min($50,000, $80,000) = $50,000
- NIIT = $50,000 × 3.8% = **$1,900**

---

## 6. Long-Term Capital Gains Tax Rates (2025)

### 6.1 Rate Thresholds by Filing Status

| Rate | Single | MFJ | MFS | Head of Household |
|------|--------|-----|-----|-------------------|
| **0%** | $0 – $48,350 | $0 – $96,700 | $0 – $48,350 | $0 – $64,750 |
| **15%** | $48,351 – $533,400 | $96,701 – $600,050 | $48,351 – $300,000 | $64,751 – $566,700 |
| **20%** | $533,401+ | $600,051+ | $300,001+ | $566,701+ |

### 6.2 Effective Rates (Including NIIT)

For taxpayers above NIIT thresholds:

| Rate | Description |
|------|-------------|
| 0% | Low income, below NIIT threshold |
| 3.8% | 0% LTCG + 3.8% NIIT |
| 15% | Mid income, below NIIT threshold |
| 18.8% | 15% LTCG + 3.8% NIIT |
| 20% | High income, below NIIT threshold |
| 23.8% | 20% LTCG + 3.8% NIIT |

### 6.3 Capital Gains Stacking

LTCG/qualified dividends "stack" on top of ordinary income:

```python
def calculate_ltcg_tax(ordinary_taxable_income: float,
                       ltcg: float,
                       filing_status: str) -> float:
    """
    Calculate tax on long-term capital gains.
    LTCG stacks on top of ordinary income for bracket determination.
    """
    brackets = get_ltcg_brackets(filing_status)  # [(48350, 0), (533400, 0.15), (inf, 0.20)]

    total_income = ordinary_taxable_income + ltcg
    tax = 0.0

    # Start where ordinary income ends
    income_position = ordinary_taxable_income
    ltcg_remaining = ltcg

    for threshold, rate in brackets:
        if income_position >= threshold:
            continue

        # How much LTCG fits in this bracket?
        bracket_space = threshold - income_position
        taxable_in_bracket = min(ltcg_remaining, bracket_space)

        tax += taxable_in_bracket * rate
        income_position += taxable_in_bracket
        ltcg_remaining -= taxable_in_bracket

        if ltcg_remaining <= 0:
            break

    return tax
```

---

## 7. Additional Medicare Tax

### 7.1 Threshold and Rate

| Filing Status | Threshold | Rate |
|---------------|-----------|------|
| Single | $200,000 | 0.9% |
| Head of Household | $200,000 | 0.9% |
| MFJ | $250,000 | 0.9% |
| MFS | $125,000 | 0.9% |

**Applies to:** Wages + self-employment income above threshold

### 7.2 Calculation

```python
def calculate_additional_medicare(wages: float,
                                  se_income: float,
                                  filing_status: str) -> float:
    threshold = get_medicare_threshold(filing_status)
    total_earned = wages + se_income

    if total_earned <= threshold:
        return 0.0

    return (total_earned - threshold) * 0.009
```

---

## 8. FICA Taxes (2025)

### 8.1 Social Security

| Component | Rate | Wage Base |
|-----------|------|-----------|
| Employee portion | 6.2% | $176,100 |
| Employer portion | 6.2% | $176,100 |
| Self-employed | 12.4% | $176,100 |

**Maximum SS tax:** $176,100 × 6.2% = $10,918.20 (employee)

### 8.2 Medicare

| Component | Rate | Wage Base |
|-----------|------|-----------|
| Employee portion | 1.45% | Unlimited |
| Employer portion | 1.45% | Unlimited |
| Additional Medicare (employee only) | 0.9% | Above $200K/$250K |
| Self-employed | 2.9% | Unlimited |

---

## 9. Withholding Rules

### 9.1 Supplemental Wage Withholding

| Income Level | Flat Rate |
|--------------|-----------|
| Up to $1 million YTD | 22% |
| Over $1 million YTD | 37% |

**Applies to:** Bonuses, RSU vesting, commission payments

### 9.2 RSU Underwithholding Example

High-income employee with:
- W-2 wages: $400,000
- RSU vest value: $100,000

**Withholding:** 22% × $100,000 = $22,000
**Actual marginal rate:** 35% (at $500,000 MFJ)
**Tax due on RSU:** 35% × $100,000 = $35,000
**Underwithholding:** $35,000 - $22,000 = **$13,000**

---

## 10. Complete Tax Calculation Workflow

```python
def calculate_total_federal_tax(
    wages: float,
    interest: float,
    dividends_ordinary: float,
    dividends_qualified: float,
    short_term_gains: float,
    long_term_gains: float,
    other_income: float,
    above_line_deductions: float,  # 401k, HSA, etc.
    itemized_deductions: float,
    filing_status: str,
    age_65_or_older: bool = False,
    blind: bool = False
) -> dict:
    """
    Complete federal tax calculation.
    """
    # Step 1: Calculate AGI
    gross_income = (wages + interest + dividends_ordinary + dividends_qualified +
                    short_term_gains + long_term_gains + other_income)
    agi = gross_income - above_line_deductions

    # Step 2: Determine deduction
    standard_deduction = get_standard_deduction(filing_status, age_65_or_older, blind)
    deduction = max(standard_deduction, itemized_deductions)

    # Step 3: Calculate taxable income
    ordinary_income = wages + interest + dividends_ordinary + short_term_gains + other_income
    ordinary_taxable = max(0, ordinary_income - above_line_deductions - deduction)

    # Step 4: Calculate ordinary income tax
    ordinary_tax = calculate_federal_tax(ordinary_taxable, filing_status)

    # Step 5: Calculate LTCG tax (stacking)
    preferential_income = dividends_qualified + long_term_gains
    ltcg_tax = calculate_ltcg_tax(ordinary_taxable, preferential_income, filing_status)

    # Step 6: Calculate AMT
    amt_adjustments = calculate_amt_adjustments(...)  # SALT, ISO, etc.
    amt = calculate_amt(ordinary_taxable + preferential_income, amt_adjustments, filing_status)

    # Step 7: Calculate NIIT
    nii = interest + dividends_ordinary + dividends_qualified + short_term_gains + long_term_gains
    niit = calculate_niit(agi, nii, filing_status)

    # Step 8: Calculate Additional Medicare Tax
    additional_medicare = calculate_additional_medicare(wages, 0, filing_status)

    # Step 9: Total tax
    total_tax = ordinary_tax + ltcg_tax + amt + niit + additional_medicare

    return {
        'agi': agi,
        'taxable_income': ordinary_taxable + preferential_income,
        'ordinary_tax': ordinary_tax,
        'ltcg_tax': ltcg_tax,
        'amt': amt,
        'niit': niit,
        'additional_medicare': additional_medicare,
        'total_federal_tax': total_tax,
        'effective_rate': total_tax / gross_income if gross_income > 0 else 0
    }
```

---

## 11. Test Cases

### 11.1 High-Income Tech Employee (MFJ)

**Inputs:**
- W-2 wages: $450,000
- RSU income (included in W-2): $150,000
- Qualified dividends: $20,000
- Long-term capital gains: $50,000
- Filing status: Married Filing Jointly
- Standard deduction: $31,500

**Expected Calculation:**
1. AGI: $520,000
2. Taxable ordinary: $520,000 - $70,000 (preferential) - $31,500 = $418,500
3. Ordinary tax: ~$92,000
4. LTCG tax: $70,000 × 15% = $10,500 (+ NIIT portion)
5. NIIT: min($70,000, $520,000 - $250,000) × 3.8% = $70,000 × 3.8% = $2,660
6. Additional Medicare: ($450,000 - $250,000) × 0.9% = $1,800
7. **Total federal tax: ~$107,000**

### 11.2 ISO Exercise AMT Scenario (Single)

**Inputs:**
- W-2 wages: $200,000
- ISO exercise: 10,000 shares × ($50 FMV - $10 strike) = $400,000 bargain element
- Filing status: Single
- Standard deduction: $15,750

**AMT Calculation:**
1. Regular taxable income: $200,000 - $15,750 = $184,250
2. Regular tax: ~$38,000
3. AMTI: $184,250 + $400,000 = $584,250
4. AMT exemption: $88,100 (no phase-out, below $626,350)
5. AMT taxable: $584,250 - $88,100 = $496,150
6. Tentative minimum tax: $119,550 × 26% + ($496,150 - $119,550) × 28% = $136,491
7. **AMT owed: $136,491 - $38,000 = $98,491**

---

## 12. Data Sources

- IRS Revenue Procedure 2024-40 (original 2025 brackets)
- One Big Beautiful Bill Act (July 4, 2025) - updated standard deductions, SALT cap
- IRS Topic 556 - Alternative Minimum Tax
- IRS Topic 559 - Net Investment Income Tax
- IRS Publication 15-T - Withholding Tables
- Tax Foundation - 2025 Tax Brackets

---

*Document generated as part of TaxLens Phase 1 Research*
