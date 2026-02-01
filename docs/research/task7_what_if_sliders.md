# Task 7: What-If Sliders - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document specifies interactive what-if scenarios for tax planning. These sliders allow users to model different tax outcomes before taking action. Key scenario categories:

1. **Equity Compensation Scenarios** (5) - RSU sales, ISO exercises, ESPP timing
2. **Income Timing Scenarios** (4) - Deferral, acceleration, bonus timing
3. **Investment Scenarios** (5) - Tax-loss harvesting, capital gains, Roth conversion
4. **State Tax Scenarios** (3) - Relocation, multi-state sourcing
5. **Retirement Scenarios** (3) - 401(k), backdoor Roth, mega backdoor
6. **Year-End Scenarios** (3) - Charitable giving, deduction bunching

---

## 1. Design Philosophy

### 1.1 Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Instant feedback** | Recalculate tax impact in <100ms |
| **Visual comparison** | Side-by-side before/after |
| **Actionable insights** | Show savings and next steps |
| **Guard rails** | Prevent unrealistic scenarios |
| **Undo/reset** | Easy return to current state |

### 1.2 UI Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│  What-If: RSU Sale Timing                                    [x]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Shares to sell:     [=====|=====] 500 shares ($200,000)           │
│                      0                              1,000           │
│                                                                     │
│  Sell in:            [Current Year] [Next Year]                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  IMPACT COMPARISON                                              ││
│  │  ────────────────────────────────────────────────────────────   ││
│  │                        Current Year    Next Year    Savings     ││
│  │  Federal Tax          $47,800          $39,400      $8,400      ││
│  │  State Tax            $21,200          $17,500      $3,700      ││
│  │  NIIT                 $2,280           $0           $2,280      ││
│  │  ─────────────────────────────────────────────────────────────  ││
│  │  Total Tax            $71,280          $56,900      $14,380     ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  [Reset]                                      [Apply to Projection] │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Equity Compensation Scenarios

### 2.1 RSU Sale Timing

**Scenario:** When should I sell vested RSU shares?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Shares to sell | Slider | 0 - Total vested shares | 0 |
| Sell timing | Toggle | Current Year / Next Year | Current |
| Holding period | Slider | 0-24 months | Current |

**Calculations:**

```python
def calculate_rsu_sale_impact(
    shares: int,
    current_price: Decimal,
    cost_basis: Decimal,
    sell_year: int,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate tax impact of RSU sale timing."""

    gain = (current_price - cost_basis) * shares
    holding_period = calculate_holding_period(cost_basis_date, sell_date)

    # Current year scenario
    current_year_income = user_data.current_year_income
    current_year_with_sale = current_year_income + gain

    current_year_tax = TaxCalculator.calculate(
        income=current_year_with_sale,
        filing_status=user_data.filing_status,
        state=user_data.state,
        capital_gains=gain if holding_period > 365 else Decimal('0'),
        short_term_gains=gain if holding_period <= 365 else Decimal('0'),
    )

    # Next year scenario (estimated)
    next_year_income = user_data.projected_next_year_income
    next_year_with_sale = next_year_income + gain

    next_year_tax = TaxCalculator.calculate(
        income=next_year_with_sale,
        filing_status=user_data.filing_status,
        state=user_data.state,
        capital_gains=gain,  # Will be LTCG if held > 1 year
    )

    return WhatIfResult(
        scenarios=[
            Scenario("Current Year", current_year_tax),
            Scenario("Next Year", next_year_tax),
        ],
        optimal="Next Year" if next_year_tax.total < current_year_tax.total else "Current Year",
        savings=abs(current_year_tax.total - next_year_tax.total),
    )
```

**Outputs:**
- Federal tax impact
- State tax impact
- NIIT impact
- WA Capital Gains impact (if applicable)
- Short-term vs long-term treatment
- Recommendation

---

### 2.2 ISO Exercise Planning

**Scenario:** How many ISOs should I exercise this year?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Shares to exercise | Slider | 0 - Exercisable shares | 0 |
| Strike price | Display | (from grant) | N/A |
| Current FMV | Input | Market price | Current |
| Same-day sale | Toggle | Yes / No | No |

**Calculations:**

```python
def calculate_iso_exercise_impact(
    shares: int,
    strike_price: Decimal,
    fmv: Decimal,
    same_day_sale: bool,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate tax impact of ISO exercise options."""

    bargain_element = (fmv - strike_price) * shares
    exercise_cost = strike_price * shares

    if same_day_sale:
        # Disqualifying disposition - ordinary income
        ordinary_income = bargain_element
        amt_adjustment = Decimal('0')
        cash_needed = Decimal('0')
        cash_generated = (fmv - strike_price) * shares
    else:
        # Hold for qualifying - AMT exposure
        ordinary_income = Decimal('0')
        amt_adjustment = bargain_element
        cash_needed = exercise_cost
        cash_generated = Decimal('0')

    # Calculate with AMT
    tax_with_amt = calculate_with_amt(
        user_data,
        amt_adjustment=amt_adjustment,
        ordinary_income=ordinary_income,
    )

    # Calculate without exercise
    tax_without = calculate_without_exercise(user_data)

    return WhatIfResult(
        scenarios=[
            Scenario("Don't Exercise", tax_without, cash_impact=Decimal('0')),
            Scenario("Exercise & Hold", tax_with_amt, cash_impact=-cash_needed),
            Scenario("Exercise & Sell", tax_same_day, cash_impact=cash_generated),
        ],
        optimal=find_optimal(scenarios),
        amt_exposure=amt_adjustment if not same_day_sale else Decimal('0'),
        qualifying_date=calculate_qualifying_date(exercise_date),
    )
```

**Outputs:**
- Regular tax impact
- AMT exposure
- Cash required to exercise
- Qualifying disposition date
- Break-even stock price
- Multi-year optimal spread

---

### 2.3 ISO Spread Across Years

**Scenario:** Spread ISO exercises over multiple years to minimize AMT.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Total shares | Display | From grants | N/A |
| Year 1 shares | Slider | 0 - Total | 0 |
| Year 2 shares | Slider | 0 - Remaining | 0 |
| Year 3 shares | Slider | 0 - Remaining | 0 |

**Outputs:**
- Total tax (3-year view)
- AMT per year
- Comparison to single-year exercise
- Optimal distribution

---

### 2.4 ESPP Sale Timing

**Scenario:** When should I sell ESPP shares?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Shares to sell | Slider | 0 - Available shares | 0 |
| Sell timing | Toggle | Now / Qualifying Date | Now |

**Calculations:**

```python
def calculate_espp_sale_impact(
    shares: int,
    purchase_price: Decimal,
    offering_price: Decimal,
    current_price: Decimal,
    purchase_date: date,
    offering_date: date,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate ESPP sale timing impact."""

    qualifying_date = max(
        offering_date + timedelta(days=730),  # 2 years from offering
        purchase_date + timedelta(days=365),  # 1 year from purchase
    )

    is_qualifying = date.today() >= qualifying_date

    if is_qualifying:
        # Qualifying disposition
        discount = offering_price * Decimal('0.15')  # Assuming 15% discount
        ordinary_income = min(discount, current_price - purchase_price)
        capital_gain = (current_price - purchase_price) - ordinary_income
    else:
        # Disqualifying disposition
        fmv_at_purchase = get_fmv_at_purchase(purchase_date)
        ordinary_income = fmv_at_purchase - purchase_price
        capital_gain = current_price - fmv_at_purchase

    return WhatIfResult(
        scenarios=[
            Scenario("Sell Now (Disqualifying)", disqualifying_tax),
            Scenario(f"Sell After {qualifying_date}", qualifying_tax),
        ],
        savings=disqualifying_tax.total - qualifying_tax.total,
        days_to_wait=(qualifying_date - date.today()).days,
    )
```

---

### 2.5 RSU vs Cash Compensation

**Scenario:** Compare tax impact of RSU vs equivalent cash compensation.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Compensation value | Input | Dollar amount | $100,000 |
| RSU growth assumption | Slider | -20% to +50% | 0% |
| Holding period | Slider | 0-24 months | 12 |

**Outputs:**
- Tax on RSU vest + sale
- Tax on equivalent cash
- Net value comparison
- Break-even growth rate

---

## 3. Income Timing Scenarios

### 3.1 Income Deferral

**Scenario:** Should I defer income to next year?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Amount to defer | Slider | $0 - $500K | $0 |
| Current year income | Display | From data | N/A |
| Next year projection | Input | Estimated | Current × 1.0 |

**Calculations:**

```python
def calculate_income_deferral(
    defer_amount: Decimal,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate tax impact of deferring income."""

    # Current year with and without deferral
    current_with = calculate_tax(user_data.income)
    current_without = calculate_tax(user_data.income - defer_amount)

    # Next year with deferred income
    next_year_projected = user_data.projected_next_year + defer_amount
    next_year_tax = calculate_tax(next_year_projected)

    total_no_defer = current_with + user_data.next_year_tax_projected
    total_with_defer = current_without + next_year_tax

    return WhatIfResult(
        scenarios=[
            Scenario("No Deferral", total_no_defer),
            Scenario("Defer to Next Year", total_with_defer),
        ],
        savings=total_no_defer - total_with_defer,
        recommendation="Defer" if total_with_defer < total_no_defer else "Don't Defer",
        consideration="Time value of money not included",
    )
```

---

### 3.2 Bonus Timing

**Scenario:** Request bonus in December vs January?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Bonus amount | Input | Dollar amount | $50,000 |
| Pay month | Toggle | December / January | December |

**Outputs:**
- Tax in current year
- Tax in next year
- Bracket impact
- NIIT threshold impact
- State tax comparison

---

### 3.3 Roth Conversion Amount

**Scenario:** How much Traditional IRA to convert to Roth?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Conversion amount | Slider | $0 - IRA balance | $0 |
| Current tax bracket | Display | From data | N/A |
| Post-conversion bracket | Display | Calculated | N/A |

**Calculations:**

```python
def calculate_roth_conversion(
    conversion_amount: Decimal,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate Roth conversion impact."""

    # Tax cost of conversion
    income_with_conversion = user_data.taxable_income + conversion_amount
    tax_with_conversion = calculate_tax(income_with_conversion)
    conversion_tax_cost = tax_with_conversion - user_data.current_tax

    # Bracket analysis
    current_bracket = get_bracket(user_data.taxable_income)
    post_conversion_bracket = get_bracket(income_with_conversion)

    # Optimal conversion (fill current bracket)
    bracket_ceiling = get_bracket_ceiling(current_bracket, user_data.filing_status)
    optimal_conversion = bracket_ceiling - user_data.taxable_income

    return WhatIfResult(
        conversion_tax_cost=conversion_tax_cost,
        current_bracket=current_bracket,
        post_conversion_bracket=post_conversion_bracket,
        optimal_conversion=optimal_conversion,
        bracket_fill_tax=calculate_tax_on_optimal(optimal_conversion),
        irmaa_impact=check_irmaa_threshold(income_with_conversion),
    )
```

**Outputs:**
- Conversion tax cost
- Before/after bracket
- Optimal "fill the bracket" amount
- IRMAA Medicare premium impact
- 10-year Roth growth projection

---

### 3.4 Self-Employment Income Scenarios

**Scenario:** Side income tax impact.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Side income | Slider | $0 - $200K | $0 |
| Business expenses | Input | Dollar amount | $0 |
| QBI deduction eligible | Toggle | Yes / No | Yes |

**Outputs:**
- Self-employment tax
- Federal income tax
- State income tax
- QBI deduction
- Net after-tax income
- Effective tax rate

---

## 4. Investment Scenarios

### 4.1 Tax-Loss Harvesting

**Scenario:** Harvest losses to offset gains.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Holdings with losses | Multi-select | From portfolio | None |
| Losses to harvest | Calculated | Sum of selected | $0 |
| Gains to offset | Display | YTD realized gains | N/A |

**Calculations:**

```python
def calculate_tlh_impact(
    losses_to_harvest: Decimal,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate tax-loss harvesting impact."""

    # Current tax on gains
    current_gains_tax = calculate_cap_gains_tax(
        user_data.ytd_realized_gains,
        user_data.filing_status,
        user_data.taxable_income,
    )

    # Tax with harvested losses
    net_gains = user_data.ytd_realized_gains - losses_to_harvest
    if net_gains < 0:
        # Apply $3,000 ordinary income offset
        ordinary_offset = min(Decimal('3000'), abs(net_gains))
        net_gains_tax = Decimal('0')
        ordinary_savings = ordinary_offset * user_data.marginal_rate
        carryforward = abs(net_gains) - ordinary_offset
    else:
        net_gains_tax = calculate_cap_gains_tax(net_gains, ...)
        ordinary_savings = Decimal('0')
        carryforward = Decimal('0')

    return WhatIfResult(
        tax_savings=current_gains_tax - net_gains_tax + ordinary_savings,
        loss_carryforward=carryforward,
        wash_sale_warning=check_wash_sale_risk(selected_holdings),
        replacement_securities=suggest_replacements(selected_holdings),
    )
```

**Outputs:**
- Tax savings
- Net gains after harvest
- Loss carryforward
- Wash sale risk warning
- Suggested replacement securities

---

### 4.2 Capital Gains Timing

**Scenario:** Realize gains this year or next?

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Gain amount | Input | Dollar amount | $0 |
| Holding period | Display | ST/LT | N/A |
| Sell timing | Toggle | This Year / Next Year | This Year |

**Outputs:**
- Tax this year vs next
- LTCG rate comparison
- WA Cap Gains impact
- NIIT impact
- Optimal timing recommendation

---

### 4.3 Charitable Stock Donation

**Scenario:** Donate appreciated stock vs cash.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Donation value | Slider | $0 - $100K | $0 |
| Stock appreciation | Display | From holdings | N/A |
| Donate | Toggle | Stock / Cash | Stock |

**Calculations:**

```python
def calculate_charitable_donation(
    donation_value: Decimal,
    stock_basis: Decimal,
    donate_stock: bool,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate charitable donation tax impact."""

    deduction_value = donation_value if itemizing(user_data) else Decimal('0')
    tax_savings_from_deduction = deduction_value * user_data.marginal_rate

    if donate_stock:
        # Avoid capital gains tax
        appreciation = donation_value - stock_basis
        cap_gains_avoided = calculate_cap_gains_tax(appreciation, ...)
        total_benefit = tax_savings_from_deduction + cap_gains_avoided
    else:
        # Cash donation - still need to sell stock to donate
        cap_gains_paid = calculate_cap_gains_tax(appreciation, ...)
        total_benefit = tax_savings_from_deduction - cap_gains_paid

    return WhatIfResult(
        tax_benefit=total_benefit,
        cap_gains_avoided=cap_gains_avoided if donate_stock else Decimal('0'),
        recommendation="Donate Stock" if donate_stock else "Donate Cash",
    )
```

---

### 4.4 Concentrated Position Diversification

**Scenario:** Sell concentrated stock position over time.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Position value | Display | From holdings | N/A |
| Sell per year | Slider | $0 - Position | $0 |
| Years to diversify | Slider | 1-5 years | 3 |

**Outputs:**
- Tax per year
- Total tax (multi-year)
- Comparison to single-year sale
- WA Cap Gains threshold management
- Portfolio risk reduction

---

### 4.5 Qualified Opportunity Zone

**Scenario:** Defer gains into QOZ investment.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Gain to defer | Input | Dollar amount | $0 |
| Investment period | Slider | 5-10+ years | 10 |

**Outputs:**
- Tax deferral value
- Basis step-up (if held 10+ years)
- Future tax liability
- Net benefit analysis

---

## 5. State Tax Scenarios

### 5.1 State Relocation Impact

**Scenario:** Tax impact of moving states.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Move from | Dropdown | States | Current |
| Move to | Dropdown | States | N/A |
| Move date | Date picker | Future date | N/A |
| Annual income | Display | From data | N/A |

**Calculations:**

```python
def calculate_relocation_impact(
    from_state: str,
    to_state: str,
    move_date: date,
    user_data: UserFinancialData
) -> WhatIfResult:
    """Calculate state relocation tax impact."""

    # Current state full year
    current_state_tax = calculate_state_tax(
        from_state,
        user_data.taxable_income,
        user_data.filing_status,
    )

    # New state full year
    new_state_tax = calculate_state_tax(
        to_state,
        user_data.taxable_income,
        user_data.filing_status,
    )

    # Split year (if moving mid-year)
    if move_date.year == date.today().year:
        days_in_old = (move_date - date(move_date.year, 1, 1)).days
        days_in_new = (date(move_date.year, 12, 31) - move_date).days
        split_year_tax = (
            current_state_tax * (days_in_old / 365) +
            new_state_tax * (days_in_new / 365)
        )
    else:
        split_year_tax = None

    # RSU sourcing impact
    rsu_sourcing_impact = calculate_rsu_sourcing(
        user_data.rsu_grants,
        from_state,
        to_state,
        move_date,
    )

    return WhatIfResult(
        current_state_annual=current_state_tax,
        new_state_annual=new_state_tax,
        annual_savings=current_state_tax - new_state_tax,
        rsu_sourcing_consideration=rsu_sourcing_impact,
        convenience_rule_warning=(from_state == "NY"),
    )
```

**Outputs:**
- Current state tax
- New state tax
- Annual savings
- RSU sourcing implications
- Multi-year projection
- Moving cost break-even

---

### 5.2 Multi-State Work Allocation

**Scenario:** Optimize work location for RSU sourcing.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Days in State A | Slider | 0-260 | Current |
| Days in State B | Slider | 0-260 | Current |
| RSU value to vest | Display | From data | N/A |

**Outputs:**
- State A tax on RSUs
- State B tax on RSUs
- Optimal allocation
- Credits available

---

### 5.3 WA Capital Gains Optimization

**Scenario:** Manage WA capital gains threshold.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Planned gains | Input | Dollar amount | $0 |
| Years to spread | Slider | 1-5 years | 1 |

**Outputs:**
- Tax with single-year sale
- Tax with multi-year spread
- Optimal annual gain target
- Deduction utilization

---

## 6. Retirement Scenarios

### 6.1 401(k) Contribution Optimization

**Scenario:** Maximize 401(k) for tax savings.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Annual contribution | Slider | $0 - $23,500 | Current |
| Catch-up (if 50+) | Slider | $0 - $7,500 | $0 |
| Pre-tax vs Roth | Toggle | Pre-tax / Roth | Pre-tax |

**Outputs:**
- Tax savings (pre-tax)
- Marginal rate comparison
- Retirement projection
- Employer match captured

---

### 6.2 Mega Backdoor Roth

**Scenario:** After-tax 401(k) to Roth conversion.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| After-tax contribution | Slider | $0 - Available | $0 |
| In-plan conversion | Toggle | Yes / No | Yes |

**Outputs:**
- Additional Roth savings
- Future tax-free growth
- Comparison to taxable investing

---

### 6.3 HSA Triple Tax Advantage

**Scenario:** Maximize HSA contributions.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| HSA contribution | Slider | $0 - Max | Current |
| Coverage type | Toggle | Individual / Family | Current |
| Invest vs save for expenses | Toggle | Invest / Spend | Invest |

**Outputs:**
- Tax savings
- FICA savings
- State tax savings
- Long-term investment growth

---

## 7. Year-End Scenarios

### 7.1 Deduction Bunching

**Scenario:** Bunch itemized deductions.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Current deductions | Display | From data | N/A |
| Additional charitable | Slider | $0 - $50K | $0 |
| Strategy | Toggle | Standard / Itemize | Auto |

**Outputs:**
- Standard vs itemized comparison
- Bunching strategy (this year vs next)
- Two-year optimization

---

### 7.2 Donor-Advised Fund

**Scenario:** Front-load charitable giving.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| DAF contribution | Input | Dollar amount | $0 |
| Appreciated stock | Toggle | Cash / Stock | Stock |

**Outputs:**
- Current year deduction
- Cap gains avoided
- Multi-year giving plan
- AGI percentage limits

---

### 7.3 Year-End Checklist Optimizer

**Scenario:** Combined year-end optimization.

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Tax-loss harvest | Toggle | Yes / No | Review |
| 401(k) max | Toggle | Yes / No | Review |
| HSA max | Toggle | Yes / No | Review |
| Charitable giving | Input | Dollar amount | $0 |

**Outputs:**
- Total tax savings
- Priority action list
- Deadlines
- Before/after tax projection

---

## 8. Implementation

### 8.1 What-If Data Model

```python
class WhatIfScenario(BaseModel):
    """What-if scenario definition."""

    scenario_id: str
    name: str
    category: ScenarioCategory
    description: str
    parameters: List[ScenarioParameter]
    calculation_function: str
    outputs: List[OutputField]


class ScenarioParameter(BaseModel):
    """Input parameter for what-if scenario."""

    param_id: str
    name: str
    type: Literal["slider", "input", "toggle", "dropdown", "date"]
    min_value: Optional[Union[Decimal, int]]
    max_value: Optional[Union[Decimal, int]]
    default_value: Union[Decimal, int, str, bool]
    step: Optional[Union[Decimal, int]]
    display_format: str  # e.g., "$0,000" or "0%"
    source_field: Optional[str]  # Field to pull default from user data


class WhatIfResult(BaseModel):
    """Result of what-if calculation."""

    scenario_id: str
    parameters_used: Dict[str, Any]
    scenarios: List[ScenarioOutcome]
    optimal: str
    savings: Decimal
    recommendation: str
    warnings: List[str]
    calculated_at: datetime


class ScenarioOutcome(BaseModel):
    """Single outcome in what-if comparison."""

    name: str
    federal_tax: Decimal
    state_tax: Decimal
    fica_tax: Decimal
    other_taxes: Dict[str, Decimal]
    total_tax: Decimal
    cash_impact: Decimal
    notes: List[str]
```

### 8.2 Performance Requirements

| Metric | Target |
|--------|--------|
| Calculation time | < 100ms |
| UI update | < 16ms (60fps) |
| Slider responsiveness | Real-time |
| Memory usage | < 50MB for scenario |

### 8.3 Calculation Caching

```python
class WhatIfCache:
    """Cache for what-if calculations."""

    def __init__(self, max_size: int = 100):
        self.cache = LRUCache(max_size)

    def get_cached(
        self,
        scenario_id: str,
        parameters: Dict[str, Any],
        user_data_hash: str
    ) -> Optional[WhatIfResult]:
        """Get cached result if parameters unchanged."""
        key = self._make_key(scenario_id, parameters, user_data_hash)
        return self.cache.get(key)

    def cache_result(
        self,
        scenario_id: str,
        parameters: Dict[str, Any],
        user_data_hash: str,
        result: WhatIfResult
    ):
        """Cache calculation result."""
        key = self._make_key(scenario_id, parameters, user_data_hash)
        self.cache.set(key, result)
```

---

## 9. Scenario Summary

| Category | # Scenarios | Key Use Cases |
|----------|-------------|---------------|
| Equity Compensation | 5 | RSU timing, ISO planning, ESPP |
| Income Timing | 4 | Deferral, bonus, Roth conversion |
| Investment | 5 | TLH, cap gains, charitable |
| State Tax | 3 | Relocation, multi-state |
| Retirement | 3 | 401(k), mega backdoor, HSA |
| Year-End | 3 | Bunching, DAF, checklist |
| **TOTAL** | **23** | |

---

## 10. Sources

### Tax Planning Software
- Holistiplan: Tax Scenario Modeling
- eMoney Pro: What-If Analysis
- Moneytree Elite: Scenario Planning

### UI/UX Patterns
- Material Design: Sliders and Controls
- Apple Human Interface Guidelines
- Financial Planning App Best Practices

### Tax Calculations
- IRS Publication 17: Your Federal Income Tax
- CCH Tax Research
- Bloomberg Tax

---

*Document generated as part of TaxLens Phase 1 Research*
