# Task 3: Equity Compensation Tax Rules - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document provides comprehensive tax rules for equity compensation types common among high-income tech professionals. Key findings:

1. **RSU taxation creates significant underwithholding** - 22% flat rate vs. actual 35-37% marginal rates
2. **ISO holders face AMT trap** - Bargain element triggers AMT even without sale
3. **ESPP has complex holding period rules** - Qualifying vs. disqualifying dispositions
4. **NSO is most straightforward** - Ordinary income at exercise, capital gains on appreciation

---

## 1. Restricted Stock Units (RSUs)

### 1.1 Taxation at Vesting

RSUs are taxed as **ordinary income** at the time of vesting, not at grant.

| Event | Tax Treatment |
|-------|---------------|
| **Grant** | No taxable event |
| **Vesting** | Fair Market Value (FMV) taxed as ordinary income |
| **Sale** | Gain/loss from vesting price taxed as capital gain |

### 1.2 Income Recognition

```
Taxable Income at Vesting = Number of Shares Vested × FMV per Share
```

**Example:**
- 100 shares vest
- FMV at vesting: $400/share
- Taxable income: $40,000 (reported on W-2)

### 1.3 Withholding Rules (Critical Gap)

| Income Level | Supplemental Withholding Rate | Actual Marginal Rate |
|--------------|------------------------------|---------------------|
| Up to $1M | **22%** | 32-37% |
| Over $1M | **37%** | 37% |

**Underwithholding Problem:**
For a tech employee in the 35% bracket with $200K RSU income:
- Withheld: $44,000 (22%)
- Actual tax: $70,000 (35%)
- **Gap: $26,000 underwitheld**

### 1.4 Withholding Methods

| Method | Description | Tax Impact |
|--------|-------------|------------|
| **Sell-to-Cover** | Company sells shares to cover taxes | Most common; taxable event |
| **Net Settlement** | Company withholds shares | Fewer shares received |
| **Cash Payment** | Employee pays tax in cash | Rare; preserves all shares |

### 1.5 Cost Basis

```
Cost Basis = FMV at Vesting Date × Number of Shares
```

This becomes important for calculating capital gains when shares are later sold.

### 1.6 Holding Period for Capital Gains

| Holding Period | Capital Gains Treatment |
|----------------|------------------------|
| ≤ 1 year from vesting | Short-term (ordinary rates) |
| > 1 year from vesting | Long-term (0%/15%/20%) |

### 1.7 Double-Counted RSU Income (Red Flag)

**Issue:** RSU income appears in both:
- W-2 Box 1 (wages)
- 1099-B (proceeds from sell-to-cover)

**Fix:** Cost basis on 1099-B should equal FMV at vesting. If broker shows $0 cost basis, user must adjust to avoid double taxation.

---

## 2. Incentive Stock Options (ISOs)

### 2.1 Taxation Overview

ISOs have **preferential tax treatment** but complex rules.

| Event | Regular Tax | AMT |
|-------|-------------|-----|
| **Grant** | No tax | No tax |
| **Exercise** | No tax | Bargain element is AMT income |
| **Qualifying Sale** | LTCG on full gain | AMT credit recovery |
| **Disqualifying Sale** | Ordinary income + LTCG | No AMT adjustment |

### 2.2 Qualifying Disposition Requirements

Both conditions must be met:
1. **2 years from grant date**
2. **1 year from exercise date**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ISO HOLDING PERIOD TIMELINE                   │
│                                                                 │
│  Grant ──────────────── Exercise ──────────────── Sale          │
│    │                       │                       │            │
│    │◄─── 2 years ──────────┼───────────────────────►            │
│                            │◄────── 1 year ────────►            │
│                                                                 │
│  Both periods must be satisfied for qualifying disposition      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Bargain Element (AMT Trap)

```
Bargain Element = (FMV at Exercise - Strike Price) × Shares Exercised
```

**Example:**
- Strike price: $50
- FMV at exercise: $150
- Shares exercised: 1,000
- Bargain element: ($150 - $50) × 1,000 = **$100,000 AMT income**

### 2.4 AMT Calculation on ISO Exercise

| Step | Calculation |
|------|-------------|
| 1. Regular taxable income | (from Form 1040) |
| 2. Add ISO bargain element | +$100,000 |
| 3. Add other AMT adjustments | +$X |
| 4. Subtract AMT exemption | -$88,100 (single 2025) |
| 5. Apply AMT rates | 26% up to $239,100, 28% above |
| 6. Compare to regular tax | Pay higher of the two |

### 2.5 AMT Credit Carryforward

If AMT paid due to ISO exercise:
- Creates **AMT credit** for future years
- Recoverable when:
  - Stock is sold (gain realized for regular tax)
  - Regular tax exceeds tentative AMT
- Credit can take many years to fully recover

### 2.6 Qualifying vs. Disqualifying Disposition

| Aspect | Qualifying | Disqualifying |
|--------|-----------|---------------|
| **Holding period** | 2yr from grant + 1yr from exercise | Either not met |
| **Ordinary income** | $0 | Lesser of: bargain element at exercise OR actual gain |
| **Capital gain** | Full gain (sale price - strike) | Remaining gain |
| **W-2 reporting** | No | Yes (ordinary income portion) |
| **AMT adjustment** | Negative (if AMT was paid) | No adjustment |

### 2.7 ISO Annual Limit

**$100,000 rule:** Only $100K worth of stock (at grant FMV) can become exercisable in any year. Excess is treated as NSO.

```
If grants exceed $100K/year:
- First $100K of FMV → ISO treatment
- Excess → NSO treatment (automatic conversion)
```

### 2.8 ISO Tax Optimization Strategies

1. **Exercise early in year** - More time to decide on same-year sale (disqualifying)
2. **Exercise in low-income years** - Minimize AMT impact
3. **Same-day sale** - Avoids AMT entirely (but disqualifying)
4. **Stagger exercises** - Spread AMT impact across years
5. **Exercise and hold 83(b)** - Not applicable to ISOs (already have it)

---

## 3. Non-Qualified Stock Options (NSOs/NQSOs)

### 3.1 Taxation Overview

NSOs have simpler but less favorable tax treatment.

| Event | Tax Treatment |
|-------|---------------|
| **Grant** | No tax (unless FMV > strike) |
| **Exercise** | Bargain element taxed as ordinary income |
| **Sale** | Gain from exercise price taxed as capital gain |

### 3.2 Income at Exercise

```
Ordinary Income = (FMV at Exercise - Strike Price) × Shares
```

**Key difference from ISO:** This is taxed immediately at exercise, not just for AMT.

### 3.3 Withholding at Exercise

| Income Level | Withholding Rate |
|--------------|------------------|
| Up to $1M | 22% (federal) + FICA |
| Over $1M | 37% (federal) + FICA |

**FICA applies to NSO income:**
- Social Security: 6.2% (up to wage base $176,100 in 2025)
- Medicare: 1.45% (no cap)
- Additional Medicare: 0.9% (over $200K/$250K)

### 3.4 Cost Basis and Holding Period

```
Cost Basis = FMV at Exercise × Shares
Holding Period: Starts at exercise date
```

### 3.5 NSO vs. ISO Comparison

| Factor | ISO | NSO |
|--------|-----|-----|
| Tax at exercise | No regular tax (AMT possible) | Ordinary income |
| FICA on spread | No | Yes |
| Holding requirement | 2yr/1yr for LTCG | 1yr for LTCG |
| $100K limit | Yes | No |
| Employer deduction | No | Yes |
| Transferable | No (except by will) | Often yes |

---

## 4. Employee Stock Purchase Plans (ESPP)

### 4.1 Plan Structure

Typical Section 423 qualified ESPP:
- **Offering period:** 6-24 months
- **Purchase period:** 6 months (often 2 per offering)
- **Discount:** Up to 15% off FMV
- **Lookback:** Purchase at lower of offering start or purchase end price
- **Contribution limit:** $25,000/year (at grant date FMV)

### 4.2 Purchase Price Calculation

```
Purchase Price = MIN(Offering Date FMV, Purchase Date FMV) × (1 - Discount%)
```

**Example:**
- Offering date FMV: $100
- Purchase date FMV: $150
- Discount: 15%
- Purchase price: MIN($100, $150) × 0.85 = **$85**
- Immediate gain: $150 - $85 = **$65/share (76% return)**

### 4.3 Qualifying vs. Disqualifying Disposition

**Qualifying Disposition Requirements (both must be met):**
1. **2 years from offering date** (enrollment/grant date)
2. **1 year from purchase date**

```
┌─────────────────────────────────────────────────────────────────┐
│                   ESPP HOLDING PERIOD TIMELINE                   │
│                                                                 │
│  Offering ────────── Purchase ────────────────── Sale           │
│  (Enroll)              Date                       │             │
│    │                    │                         │             │
│    │◄────── 2 years ────┼─────────────────────────►             │
│                         │◄─────── 1 year ─────────►             │
│                                                                 │
│  Both periods must be satisfied for qualifying disposition      │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Tax Treatment Comparison

| Aspect | Qualifying Disposition | Disqualifying Disposition |
|--------|----------------------|--------------------------|
| **Ordinary income** | Lesser of: (1) discount at offering, or (2) actual gain | Bargain element (FMV at purchase - purchase price) |
| **Capital gain** | Remaining gain | Sale price - FMV at purchase |
| **W-2 reporting** | No | Yes |

### 4.5 Qualifying Disposition Example

**Facts:**
- Offering date FMV: $100
- Purchase date FMV: $150
- Purchase price: $85 (15% discount on $100)
- Sale price: $200 (after holding period met)

**Calculation:**
```
Discount at offering = $100 × 15% = $15/share
Actual gain = $200 - $85 = $115/share

Ordinary income = MIN($15, $115) = $15/share
Capital gain = $200 - $85 - $15 = $100/share (LTCG)
```

### 4.6 Disqualifying Disposition Example

**Same facts, but sold within 1 year of purchase:**

**Calculation:**
```
Bargain element = $150 - $85 = $65/share (ordinary income)
Capital gain = $200 - $150 = $50/share (STCG if < 1yr from purchase)
```

**Note:** Disqualifying disposition often results in MORE ordinary income and LESS capital gain.

### 4.7 ESPP Loss Scenario

If stock declines below purchase price:
- **Qualifying:** Report loss = offering date discount (ordinary income) + capital loss
- **Disqualifying:** Only capital loss (no ordinary income since no bargain at sale)

### 4.8 Cost Basis Complexity

| Disposition Type | Cost Basis |
|------------------|-----------|
| Qualifying | Purchase price + ordinary income recognized |
| Disqualifying | FMV at purchase date |

---

## 5. Tax Withholding Summary

### 5.1 Withholding Rates by Equity Type

| Equity Type | Event | Federal | FICA | State (CA) |
|-------------|-------|---------|------|------------|
| **RSU** | Vesting | 22%/37% | 7.65% | ~10% |
| **ISO** | Exercise | None | None | None |
| **ISO** | Disqual. Sale | None (but owe) | None | None |
| **NSO** | Exercise | 22%/37% | 7.65% | ~10% |
| **ESPP** | Purchase | None | None | None |
| **ESPP** | Disqual. Sale | None (but owe) | None | None |

### 5.2 Underwithholding Calculator

```python
def calculate_underwithholding(equity_income: Decimal,
                               other_income: Decimal,
                               filing_status: str) -> Decimal:
    """
    Calculate expected underwithholding from equity compensation.

    Args:
        equity_income: RSU/NSO income subject to 22% withholding
        other_income: W-2 salary and other income
        filing_status: 'single', 'married_jointly', etc.

    Returns:
        Expected additional tax owed (positive) or refund (negative)
    """
    # Get marginal rate for total income
    total_income = equity_income + other_income
    marginal_rate = get_marginal_rate(total_income, filing_status)

    # Withholding on equity (22% for income under $1M)
    if equity_income <= 1_000_000:
        withheld = equity_income * Decimal('0.22')
    else:
        withheld = (1_000_000 * Decimal('0.22') +
                   (equity_income - 1_000_000) * Decimal('0.37'))

    # Actual tax on equity income (at marginal rate)
    actual_tax = equity_income * marginal_rate

    return actual_tax - withheld
```

---

## 6. State Tax Considerations

### 6.1 California Specific Rules

| Rule | Detail |
|------|--------|
| No LTCG preference | All gains taxed at ordinary rates (up to 13.3%) |
| RSU vesting | Taxed if working in CA when shares vest |
| ISO exercise | No AMT adjustment (CA has no AMT) |
| Multi-state sourcing | Allocation based on work days in CA during vesting period |

### 6.2 California Sourcing for RSUs

```
CA Taxable RSU Income = Total RSU Income × (CA Work Days / Total Work Days During Vest Period)
```

**Example:**
- Total RSU income: $100,000
- Vesting period: 4 years (1,040 work days)
- Work days in CA: 780 (moved to WA last year)
- CA taxable: $100,000 × (780/1,040) = **$75,000**

### 6.3 Washington State Rules

| Rule | Detail |
|------|--------|
| No state income tax | No tax on RSU/ISO/NSO/ESPP income |
| WA Capital Gains Tax | 7% on LTCG over $270K (2025) |
| ISO exercise | No state AMT concern |
| ESPP gains | May be subject to WA cap gains if LTCG portion > threshold |

---

## 7. TaxLens Implementation Requirements

### 7.1 Data Fields Needed

**RSU Tracking:**
```python
class RSUGrant:
    grant_id: str
    grant_date: date
    total_shares: int
    vested_shares: int
    unvested_shares: int
    vesting_schedule: List[VestingEvent]  # (date, shares)
    fmv_at_grant: Decimal

class RSUVest:
    vest_id: str
    grant_id: str
    vest_date: date
    shares_vested: int
    fmv_at_vest: Decimal
    withheld_shares: int
    withheld_cash: Decimal
    net_shares: int
    cost_basis: Decimal  # FMV × shares
```

**ISO Tracking:**
```python
class ISOGrant:
    grant_id: str
    grant_date: date
    expiration_date: date
    total_shares: int
    strike_price: Decimal
    exercised_shares: int
    remaining_shares: int

class ISOExercise:
    exercise_id: str
    grant_id: str
    exercise_date: date
    shares_exercised: int
    fmv_at_exercise: Decimal
    strike_price: Decimal
    bargain_element: Decimal  # (FMV - strike) × shares
    amt_adjustment: Decimal
    qualifying_sale_date: date  # 1yr from exercise
    full_qualifying_date: date  # 2yr from grant
```

**ESPP Tracking:**
```python
class ESPPPurchase:
    purchase_id: str
    offering_date: date
    purchase_date: date
    shares_purchased: int
    offering_price: Decimal  # FMV at offering
    purchase_price: Decimal  # Discounted price paid
    fmv_at_purchase: Decimal
    discount_percent: Decimal
    qualifying_sale_date: date  # 1yr from purchase
    full_qualifying_date: date  # 2yr from offering
```

### 7.2 Calculations Required

1. **RSU underwithholding projection**
2. **ISO AMT impact calculator**
3. **ISO qualifying disposition date tracker**
4. **ESPP ordinary income calculator** (both scenarios)
5. **ESPP holding period tracker**
6. **Multi-state sourcing for CA residents**
7. **WA capital gains threshold monitoring**

### 7.3 Red Flags to Detect

| Red Flag | Condition |
|----------|-----------|
| RSU underwithholding | Total RSU income × (marginal rate - 22%) > $5,000 |
| ISO AMT trigger | Bargain element + AMTI > AMT exemption |
| ISO disqualifying sale imminent | Sale within 1yr of exercise or 2yr of grant |
| ESPP disqualifying sale | Sale before qualifying dates |
| Double-counted RSU income | 1099-B shows $0 cost basis for RSU shares |
| Large ISO exercise without sale | Exercise creates AMT with no cash to pay |
| $100K ISO limit exceeded | Exercisable ISOs > $100K FMV in any year |

---

## 8. Special Scenarios

### 8.1 83(b) Election (Early Exercise)

For **stock options** or **restricted stock** (not RSUs):
- Elect to be taxed at grant rather than vesting
- Must file within 30 days of grant
- Locks in lower FMV for tax purposes
- Risk: If you leave or stock tanks, tax paid on unvested shares

**Not applicable to RSUs** - RSUs are always taxed at vesting.

### 8.2 Net Issuance (ISO Strategy)

Exercise ISOs using existing shares rather than cash:
- Reduces cash outlay
- Can defer recognition
- Complex basis tracking required

### 8.3 Cashless Exercise

For NSOs, can exercise and immediately sell:
- No cash outlay required
- Entire spread taxed as ordinary income
- Simple but loses LTCG potential

### 8.4 Stock Swaps

Exchange existing shares for option exercise:
- Defers gain on exchanged shares
- Complex basis layering
- Tacked holding period on exchanged portion

---

## 9. Form Requirements

### 9.1 Employer Forms

| Form | Equity Type | Purpose |
|------|-------------|---------|
| **W-2** | RSU, NSO, Disq. ESPP | Reports ordinary income, withholding |
| **3921** | ISO | Reports ISO exercise (for AMT) |
| **3922** | ESPP | Reports ESPP purchase details |

### 9.2 Individual Tax Forms

| Form | Use |
|------|-----|
| **Form 8949** | Report sales (capital gains/losses) |
| **Schedule D** | Summary of capital gains |
| **Form 6251** | AMT calculation (if applicable) |
| **Form 8801** | AMT credit (if prior year AMT paid) |

---

## 10. Sources

### IRS Publications
- IRS Publication 525: Taxable and Nontaxable Income
- IRS Publication 551: Basis of Assets
- IRS Form 3921/3922 Instructions
- IRC Section 83 (Property Transferred in Connection with Performance of Services)
- IRC Section 421-424 (Incentive Stock Options)
- IRC Section 423 (Employee Stock Purchase Plans)

### Industry Resources
- Charles Schwab Equity Compensation Guide
- Fidelity Stock Plan Services Tax Guide
- E*TRADE Stock Plan Education Center
- Morgan Stanley at Work Tax Resources

### Tax Research
- AICPA: Equity Compensation Tax Issues
- Journal of Accountancy: Stock Option Taxation
- Tax Foundation: Capital Gains Research

---

*Document generated as part of TaxLens Phase 1 Research*
