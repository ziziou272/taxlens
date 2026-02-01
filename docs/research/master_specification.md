# TaxLens: Master Product Specification

## AI-Powered Tax Intelligence for High-Income Tech Professionals

**Version:** 1.0
**Date:** January 2026
**Target Users:** Tech employees earning $200K-$1M+ with equity compensation
**Markets:** California, New York, Washington State (initial)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Market Analysis & Competitive Landscape](#2-market-analysis--competitive-landscape)
3. [Core Tax Calculation Engine](#3-core-tax-calculation-engine)
4. [Equity Compensation Module](#4-equity-compensation-module)
5. [Multi-State Tax Engine](#5-multi-state-tax-engine)
6. [Data Integration Architecture](#6-data-integration-architecture)
7. [Red Flag Alert System](#7-red-flag-alert-system)
8. [What-If Scenario Engine](#8-what-if-scenario-engine)
9. [Technical Architecture](#9-technical-architecture)
10. [Privacy & Security Framework](#10-privacy--security-framework)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Appendices](#12-appendices)

---

## 1. Executive Summary

### 1.1 Product Vision

TaxLens is an AI-powered tax intelligence platform designed specifically for high-income tech professionals with complex equity compensation. Unlike generic tax software that focuses on tax filing, TaxLens provides **year-round proactive tax planning** with real-time alerts, what-if scenario modeling, and AI-driven recommendations.

### 1.2 Core Value Propositions

| Value | Description | User Benefit |
|-------|-------------|--------------|
| **Proactive Alerts** | 73+ automated tax alerts | Avoid costly mistakes before they happen |
| **Equity Intelligence** | RSU, ISO, NSO, ESPP optimization | Maximize after-tax value of equity comp |
| **Multi-State Mastery** | CA, NY, WA specific calculations | Accurate state tax planning |
| **What-If Modeling** | Interactive scenario analysis | Make informed financial decisions |
| **AI Recommendations** | Personalized tax strategies | Actionable insights, not just data |

### 1.3 Target User Profile

```
PRIMARY PERSONA: "Tech Executive with Equity"
├── Income: $200K - $1M+ (W-2 + equity)
├── Equity: RSUs, ISOs, NSOs, ESPP across 1-3 companies
├── Location: CA, NY, or WA (remote work complexity)
├── Pain Points:
│   ├── Underwithholding surprises ($10K-$50K+ tax bills)
│   ├── AMT triggers from ISO exercises
│   ├── Multi-state sourcing complexity
│   ├── Capital gains optimization (WA 7% threshold)
│   └── Tax-loss harvesting coordination with equity
└── Current Solutions: Spreadsheets, generic TurboTax, expensive CPAs
```

### 1.4 Market Opportunity

- **TAM:** 2.5M+ tech employees with equity compensation in US
- **SAM:** 500K+ in CA/NY/WA earning $200K+
- **SOM:** 50K users at $99-299/year = $5M-15M ARR potential

### 1.5 Competitive Advantage

| Competitor | Limitation | TaxLens Advantage |
|------------|------------|-------------------|
| TurboTax | Filing-focused, reactive | Year-round proactive planning |
| H&R Block | Generic, no equity expertise | Deep equity compensation intelligence |
| TaxAct | Basic, limited scenarios | Advanced what-if modeling |
| CPAs | Expensive ($500+/hr), slow | Instant AI-powered analysis |
| Spreadsheets | Manual, error-prone | Automated, always accurate |

---

## 2. Market Analysis & Competitive Landscape

### 2.1 Existing Solutions Analysis

#### Consumer Tax Software
- **TurboTax Premier/Self-Employed:** $90-170/year, strong stock sale import but reactive, filing-focused
- **H&R Block Premium:** $55-110/year, basic investment support, no equity optimization
- **TaxAct Premier:** $40-70/year, cost-effective but limited scenario modeling

#### Equity-Focused Tools
- **Secfi:** Equity financing focus, not tax planning
- **Carta:** Cap table management, limited tax intelligence
- **Harness Wealth:** Advisor marketplace, not self-service

#### Financial Aggregators
- **Monarch Money:** Excellent aggregation, no tax intelligence
- **Copilot:** Modern UI, basic tax estimates
- **YNAB:** Budgeting focus, no tax features

### 2.2 Gap Analysis

```
MARKET GAPS TAXLENS ADDRESSES:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  1. PROACTIVE vs REACTIVE                                          │
│     ├── Competitors: Wait until filing season                      │
│     └── TaxLens: Year-round monitoring and alerts                  │
│                                                                     │
│  2. EQUITY INTELLIGENCE                                            │
│     ├── Competitors: Generic stock sale handling                   │
│     └── TaxLens: RSU/ISO/NSO/ESPP optimization engine             │
│                                                                     │
│  3. MULTI-STATE COMPLEXITY                                         │
│     ├── Competitors: Simple state selection                        │
│     └── TaxLens: Automatic sourcing calculations                   │
│                                                                     │
│  4. WHAT-IF SCENARIOS                                              │
│     ├── Competitors: Static calculations                           │
│     └── TaxLens: Interactive sliders with real-time updates       │
│                                                                     │
│  5. AI-POWERED RECOMMENDATIONS                                     │
│     ├── Competitors: Generic tips                                  │
│     └── TaxLens: Personalized, actionable strategies              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Tax Calculation Engine

### 3.1 Federal Tax Calculations (2025 Rules)

#### Tax Bracket Engine

```python
FEDERAL_BRACKETS_2025 = {
    "single": [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (626_350, 0.35),
        (float('inf'), 0.37),
    ],
    "married_jointly": [
        (23_850, 0.10),
        (96_950, 0.12),
        (206_700, 0.22),
        (394_600, 0.24),
        (501_050, 0.32),
        (751_600, 0.35),
        (float('inf'), 0.37),
    ],
}

def calculate_federal_tax(taxable_income: Decimal, filing_status: str) -> Decimal:
    """Calculate federal income tax using 2025 brackets."""
    brackets = FEDERAL_BRACKETS_2025[filing_status]
    tax = Decimal("0")
    prev_threshold = Decimal("0")

    for threshold, rate in brackets:
        if taxable_income <= prev_threshold:
            break
        taxable_in_bracket = min(taxable_income, Decimal(str(threshold))) - prev_threshold
        tax += taxable_in_bracket * Decimal(str(rate))
        prev_threshold = Decimal(str(threshold))

    return tax.quantize(Decimal("0.01"))
```

#### Standard Deductions (2025)

| Filing Status | Standard Deduction |
|---------------|-------------------|
| Single | $15,000 |
| Married Filing Jointly | $30,000 |
| Married Filing Separately | $15,000 |
| Head of Household | $22,500 |

#### Alternative Minimum Tax (AMT)

```python
AMT_CONFIG_2025 = {
    "exemption": {
        "single": 88_100,
        "married_jointly": 137_000,
    },
    "phaseout_start": {
        "single": 626_350,
        "married_jointly": 1_252_700,
    },
    "rates": [(232_600, 0.26), (float('inf'), 0.28)],
}

def calculate_amt(
    regular_taxable_income: Decimal,
    iso_bargain_element: Decimal,
    filing_status: str
) -> Decimal:
    """Calculate AMT liability."""
    amti = regular_taxable_income + iso_bargain_element
    exemption = calculate_amt_exemption(amti, filing_status)
    amt_taxable = max(Decimal("0"), amti - exemption)
    amt_tax = apply_amt_rates(amt_taxable)
    return amt_tax
```

#### Net Investment Income Tax (NIIT)

```python
NIIT_CONFIG = {
    "rate": Decimal("0.038"),
    "thresholds": {
        "single": 200_000,
        "married_jointly": 250_000,
        "married_separately": 125_000,
    }
}

def calculate_niit(
    magi: Decimal,
    net_investment_income: Decimal,
    filing_status: str
) -> Decimal:
    """Calculate 3.8% NIIT on investment income above threshold."""
    threshold = NIIT_CONFIG["thresholds"][filing_status]
    excess_magi = max(Decimal("0"), magi - threshold)
    niit_base = min(excess_magi, net_investment_income)
    return (niit_base * NIIT_CONFIG["rate"]).quantize(Decimal("0.01"))
```

#### Capital Gains Tax

```python
LTCG_BRACKETS_2025 = {
    "single": [
        (48_350, Decimal("0.00")),
        (533_400, Decimal("0.15")),
        (float('inf'), Decimal("0.20")),
    ],
    "married_jointly": [
        (96_700, Decimal("0.00")),
        (600_050, Decimal("0.15")),
        (float('inf'), Decimal("0.20")),
    ],
}

def calculate_capital_gains_tax(
    ordinary_income: Decimal,
    short_term_gains: Decimal,
    long_term_gains: Decimal,
    filing_status: str
) -> CapitalGainsTax:
    """Calculate tax on capital gains."""
    # Short-term: taxed as ordinary income
    stcg_tax = calculate_marginal_tax(short_term_gains, ordinary_income, filing_status)

    # Long-term: preferential rates
    ltcg_tax = calculate_ltcg_tax(long_term_gains, ordinary_income, filing_status)

    return CapitalGainsTax(
        short_term_tax=stcg_tax,
        long_term_tax=ltcg_tax,
        total=stcg_tax + ltcg_tax,
    )
```

### 3.2 Employment Taxes (FICA)

```python
FICA_CONFIG_2025 = {
    "social_security": {
        "rate": Decimal("0.062"),
        "wage_base": 176_100,  # 2025 limit
    },
    "medicare": {
        "rate": Decimal("0.0145"),
        "additional_rate": Decimal("0.009"),  # Above threshold
        "additional_threshold": {
            "single": 200_000,
            "married_jointly": 250_000,
        }
    }
}

def calculate_fica(
    wages: Decimal,
    ytd_wages: Decimal,
    filing_status: str
) -> FICATax:
    """Calculate Social Security and Medicare taxes."""
    # Social Security (up to wage base)
    ss_taxable = min(wages, max(Decimal("0"),
                    Decimal(str(FICA_CONFIG_2025["social_security"]["wage_base"])) - ytd_wages))
    ss_tax = ss_taxable * FICA_CONFIG_2025["social_security"]["rate"]

    # Medicare (uncapped)
    medicare_tax = wages * FICA_CONFIG_2025["medicare"]["rate"]

    # Additional Medicare (above threshold)
    threshold = FICA_CONFIG_2025["medicare"]["additional_threshold"][filing_status]
    if ytd_wages + wages > threshold:
        additional_base = max(Decimal("0"), wages - max(Decimal("0"), threshold - ytd_wages))
        medicare_tax += additional_base * FICA_CONFIG_2025["medicare"]["additional_rate"]

    return FICATax(
        social_security=ss_tax.quantize(Decimal("0.01")),
        medicare=medicare_tax.quantize(Decimal("0.01")),
    )
```

---

## 4. Equity Compensation Module

### 4.1 RSU (Restricted Stock Units)

#### Taxation Rules
- **At Vesting:** FMV taxed as ordinary income (W-2)
- **At Sale:** Difference between sale price and FMV at vest is capital gain/loss
- **Holding Period:** Starts at vesting date

```python
class RSUTaxCalculator:
    """Calculate tax implications of RSU vesting and sale."""

    SUPPLEMENTAL_RATE = Decimal("0.22")  # Up to $1M
    EXCESS_SUPPLEMENTAL_RATE = Decimal("0.37")  # Above $1M

    def calculate_vest_withholding(
        self,
        shares: int,
        fmv_per_share: Decimal,
        ytd_supplemental_income: Decimal
    ) -> RSUVestWithholding:
        """Calculate withholding at RSU vest."""
        vest_value = shares * fmv_per_share

        # Federal supplemental withholding
        if ytd_supplemental_income + vest_value <= 1_000_000:
            federal_rate = self.SUPPLEMENTAL_RATE
        else:
            # Blended rate for amount crossing $1M threshold
            below_threshold = max(Decimal("0"), 1_000_000 - ytd_supplemental_income)
            above_threshold = vest_value - below_threshold
            federal_withholding = (below_threshold * self.SUPPLEMENTAL_RATE +
                                  above_threshold * self.EXCESS_SUPPLEMENTAL_RATE)
            federal_rate = federal_withholding / vest_value

        return RSUVestWithholding(
            gross_value=vest_value,
            federal_withholding=vest_value * federal_rate,
            social_security=self._calc_ss(vest_value),
            medicare=vest_value * Decimal("0.0145"),
            state_withholding=self._calc_state(vest_value),
            net_shares=self._shares_after_withholding(shares, fmv_per_share),
        )

    def calculate_sale_tax(
        self,
        shares_sold: int,
        sale_price: Decimal,
        vest_fmv: Decimal,
        vest_date: date,
        sale_date: date
    ) -> RSUSaleTax:
        """Calculate capital gains tax on RSU sale."""
        proceeds = shares_sold * sale_price
        cost_basis = shares_sold * vest_fmv
        gain_loss = proceeds - cost_basis

        holding_period = (sale_date - vest_date).days
        is_long_term = holding_period > 365

        return RSUSaleTax(
            proceeds=proceeds,
            cost_basis=cost_basis,
            gain_loss=gain_loss,
            holding_period_days=holding_period,
            is_long_term=is_long_term,
            tax_type="LTCG" if is_long_term else "STCG",
        )
```

### 4.2 ISO (Incentive Stock Options)

#### Taxation Rules
- **At Exercise:** No regular tax, but spread is AMT preference item
- **At Sale (Qualifying):** All gain is LTCG (hold 2 years from grant, 1 year from exercise)
- **At Sale (Disqualifying):** Spread at exercise is ordinary income

```python
class ISOTaxCalculator:
    """Calculate ISO exercise and sale tax implications."""

    def calculate_exercise_impact(
        self,
        shares: int,
        exercise_price: Decimal,
        fmv_at_exercise: Decimal,
        existing_amti: Decimal,
        filing_status: str
    ) -> ISOExerciseImpact:
        """Calculate AMT impact of ISO exercise."""
        bargain_element = shares * (fmv_at_exercise - exercise_price)

        # AMT calculation
        amti_before = existing_amti
        amti_after = existing_amti + bargain_element

        amt_before = self.calculate_amt(amti_before, filing_status)
        amt_after = self.calculate_amt(amti_after, filing_status)

        amt_increase = amt_after - amt_before

        return ISOExerciseImpact(
            bargain_element=bargain_element,
            amt_preference_item=bargain_element,
            amt_before=amt_before,
            amt_after=amt_after,
            additional_amt_liability=amt_increase,
            breakeven_price=self._calc_breakeven(exercise_price, amt_increase, shares),
        )

    def calculate_sale_tax(
        self,
        shares: int,
        exercise_price: Decimal,
        fmv_at_exercise: Decimal,
        sale_price: Decimal,
        grant_date: date,
        exercise_date: date,
        sale_date: date
    ) -> ISOSaleTax:
        """Determine qualifying vs disqualifying disposition."""
        years_from_grant = (sale_date - grant_date).days / 365
        years_from_exercise = (sale_date - exercise_date).days / 365

        is_qualifying = years_from_grant >= 2 and years_from_exercise >= 1

        if is_qualifying:
            # All gain is LTCG
            return ISOSaleTax(
                disposition_type="qualifying",
                ordinary_income=Decimal("0"),
                capital_gain=shares * (sale_price - exercise_price),
                capital_gain_type="LTCG",
            )
        else:
            # Bargain element is ordinary income
            bargain = shares * (fmv_at_exercise - exercise_price)
            additional_gain = shares * (sale_price - fmv_at_exercise)

            return ISOSaleTax(
                disposition_type="disqualifying",
                ordinary_income=bargain,
                capital_gain=additional_gain,
                capital_gain_type="STCG" if years_from_exercise < 1 else "LTCG",
            )
```

### 4.3 NSO (Non-Qualified Stock Options)

```python
class NSOTaxCalculator:
    """Calculate NSO tax implications."""

    def calculate_exercise_tax(
        self,
        shares: int,
        exercise_price: Decimal,
        fmv_at_exercise: Decimal
    ) -> NSOExerciseTax:
        """Calculate tax at NSO exercise."""
        bargain_element = shares * (fmv_at_exercise - exercise_price)

        return NSOExerciseTax(
            bargain_element=bargain_element,
            ordinary_income=bargain_element,  # Taxed immediately
            federal_withholding=self._calc_federal_withholding(bargain_element),
            fica_withholding=self._calc_fica(bargain_element),
            state_withholding=self._calc_state(bargain_element),
        )
```

### 4.4 ESPP (Employee Stock Purchase Plan)

```python
class ESPPTaxCalculator:
    """Calculate ESPP tax implications."""

    def calculate_sale_tax(
        self,
        shares: int,
        purchase_price: Decimal,
        fmv_at_offering: Decimal,
        fmv_at_purchase: Decimal,
        sale_price: Decimal,
        offering_date: date,
        purchase_date: date,
        sale_date: date
    ) -> ESPPSaleTax:
        """Calculate ESPP disposition tax."""
        years_from_offering = (sale_date - offering_date).days / 365
        years_from_purchase = (sale_date - purchase_date).days / 365

        is_qualifying = years_from_offering >= 2 and years_from_purchase >= 1

        discount = fmv_at_purchase - purchase_price

        if is_qualifying:
            # Ordinary income limited to actual discount
            ordinary_income = min(discount, fmv_at_offering * Decimal("0.15"))
            capital_gain = shares * (sale_price - purchase_price) - ordinary_income
            return ESPPSaleTax(
                disposition_type="qualifying",
                ordinary_income=ordinary_income,
                capital_gain=capital_gain,
                capital_gain_type="LTCG",
            )
        else:
            # Full discount is ordinary income
            return ESPPSaleTax(
                disposition_type="disqualifying",
                ordinary_income=discount * shares,
                capital_gain=shares * (sale_price - fmv_at_purchase),
                capital_gain_type="STCG" if years_from_purchase < 1 else "LTCG",
            )
```

---

## 5. Multi-State Tax Engine

### 5.1 State Tax Brackets (2025)

#### California

```python
CA_BRACKETS_2025 = {
    "single": [
        (10_756, Decimal("0.01")),
        (25_499, Decimal("0.02")),
        (40_245, Decimal("0.04")),
        (55_866, Decimal("0.06")),
        (70_606, Decimal("0.08")),
        (360_659, Decimal("0.093")),
        (432_787, Decimal("0.103")),
        (721_314, Decimal("0.113")),
        (float('inf'), Decimal("0.123")),
    ],
}

# Mental Health Services Tax: +1% on income over $1M
CA_MENTAL_HEALTH_TAX = {
    "threshold": 1_000_000,
    "rate": Decimal("0.01"),
}

# SDI: 1.1% on wages up to $153,164
CA_SDI_2025 = {
    "rate": Decimal("0.011"),
    "wage_limit": 153_164,
}
```

#### New York

```python
NY_BRACKETS_2025 = {
    "single": [
        (8_500, Decimal("0.04")),
        (11_700, Decimal("0.045")),
        (13_900, Decimal("0.0525")),
        (80_650, Decimal("0.0585")),
        (215_400, Decimal("0.0625")),
        (1_077_550, Decimal("0.0685")),
        (5_000_000, Decimal("0.0965")),
        (25_000_000, Decimal("0.103")),
        (float('inf'), Decimal("0.109")),
    ],
}

# NYC Resident Tax (additional)
NYC_BRACKETS_2025 = {
    "single": [
        (12_000, Decimal("0.03078")),
        (25_000, Decimal("0.03762")),
        (50_000, Decimal("0.03819")),
        (float('inf'), Decimal("0.03876")),
    ],
}
```

#### Washington State

```python
WA_TAX_CONFIG_2025 = {
    "income_tax": None,  # No state income tax

    "capital_gains_tax": {
        "rate_tier_1": Decimal("0.07"),      # 7% up to $1M
        "rate_tier_2": Decimal("0.099"),     # 9.9% above $1M (proposed)
        "threshold": 270_000,                 # 2025 threshold
        "exempt_types": [
            "retirement_accounts",
            "real_estate",
            "qualified_small_business_stock",
        ],
    },

    "long_term_care": {
        "rate": Decimal("0.0058"),  # 0.58% on W-2 wages
        "applies_to": "W-2 only",
    },
}
```

### 5.2 Multi-State RSU Sourcing

```python
class MultiStateRSUSourcing:
    """Calculate RSU income allocation across states."""

    def calculate_allocation(
        self,
        grant_date: date,
        vest_date: date,
        work_history: List[WorkPeriod]
    ) -> Dict[str, Decimal]:
        """
        Allocate RSU income based on workdays in each state.

        Standard Method: Pro-rata based on grant-to-vest workdays
        """
        total_days = (vest_date - grant_date).days
        state_days = defaultdict(int)

        for period in work_history:
            if period.start_date > vest_date or period.end_date < grant_date:
                continue

            overlap_start = max(period.start_date, grant_date)
            overlap_end = min(period.end_date, vest_date)
            days_in_period = (overlap_end - overlap_start).days
            state_days[period.state] += days_in_period

        allocations = {}
        for state, days in state_days.items():
            allocations[state] = Decimal(str(days / total_days))

        return allocations

    def calculate_multi_state_tax(
        self,
        rsu_income: Decimal,
        allocations: Dict[str, Decimal],
        resident_state: str
    ) -> MultiStateTaxResult:
        """Calculate tax liability in each state with credits."""
        taxes = {}
        credits = {}

        for state, allocation in allocations.items():
            state_income = rsu_income * allocation
            taxes[state] = self.calculate_state_tax(state, state_income)

            # Resident state credit for taxes paid to other states
            if state != resident_state:
                credits[state] = min(
                    taxes[state],
                    self.calculate_state_tax(resident_state, state_income)
                )

        return MultiStateTaxResult(
            state_taxes=taxes,
            other_state_credits=credits,
            resident_state_credit=sum(credits.values()),
        )
```

---

## 6. Data Integration Architecture

### 6.1 Plaid Integration

#### Investment Holdings API

```python
class PlaidInvestmentSync:
    """Sync investment data from Plaid."""

    async def sync_holdings(self, access_token: str) -> List[Holding]:
        """Fetch current investment holdings."""
        response = await self.client.investments_holdings_get(
            InvestmentsHoldingsGetRequest(access_token=access_token)
        )

        holdings = []
        for holding in response.holdings:
            security = self._get_security(response.securities, holding.security_id)

            holdings.append(Holding(
                symbol=security.ticker_symbol,
                name=security.name,
                quantity=holding.quantity,
                price=holding.institution_price,
                value=holding.institution_value,
                cost_basis=holding.cost_basis,
                unrealized_gain=(holding.institution_value - holding.cost_basis)
                    if holding.cost_basis else None,
                security_type=security.type,
                is_cash_equivalent=security.is_cash_equivalent,
            ))

        return holdings

    async def sync_transactions(
        self,
        access_token: str,
        start_date: date,
        end_date: date
    ) -> List[InvestmentTransaction]:
        """Fetch investment transactions for tax lot tracking."""
        response = await self.client.investments_transactions_get(
            InvestmentsTransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            )
        )

        return [
            InvestmentTransaction(
                date=txn.date,
                type=txn.type,  # buy, sell, dividend, etc.
                symbol=self._get_symbol(response.securities, txn.security_id),
                quantity=txn.quantity,
                price=txn.price,
                amount=txn.amount,
                fees=txn.fees,
            )
            for txn in response.investment_transactions
        ]
```

#### Data Mapping

| Plaid Field | TaxLens Field | Tax Use |
|-------------|---------------|---------|
| `holding.cost_basis` | `tax_lot.cost_basis` | Capital gains calculation |
| `holding.quantity` | `position.shares` | Holdings tracking |
| `transaction.type=sell` | `sale.proceeds` | 1099-B reconciliation |
| `transaction.type=dividend` | `dividend.amount` | 1099-DIV tracking |

### 6.2 Document Intelligence (Claude Vision)

#### Extraction Pipeline

```python
class DocumentExtractor:
    """Extract structured data from tax documents using Claude Vision."""

    async def extract(self, document: UploadedDocument) -> ExtractedData:
        """Process document through Claude Vision."""

        # 1. Load document-specific prompt
        prompt = self.load_prompt(document.type)

        # 2. Call Claude API
        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": document.to_base64(),
                        },
                    },
                    {"type": "text", "text": prompt}
                ],
            }],
        )

        # 3. Parse and validate
        extracted = self.parse_response(response.content[0].text, document.type)
        validated = self.validate(extracted, document.type)

        return validated
```

#### Supported Document Types

| Document | Key Fields | Accuracy Target |
|----------|------------|-----------------|
| W-2 | Box 1-14, employer info | 99%+ |
| 1099-B | Proceeds, cost basis, dates | 98%+ |
| 1099-DIV | Ordinary/qualified dividends | 99%+ |
| Form 3921 | ISO exercise details | 98%+ |
| Form 3922 | ESPP transfer details | 98%+ |
| Pay Stub | YTD income, withholding | 95%+ |

---

## 7. Red Flag Alert System

### 7.1 Alert Categories (73 Total)

| Category | Count | Examples |
|----------|-------|----------|
| Underwithholding | 12 | Critical gap, supplemental shortfall |
| AMT | 10 | ISO exercise trigger, AMT crossover |
| Capital Gains | 11 | Wash sale, WA threshold breach |
| Equity Compensation | 14 | ISO deadline, ESPP qualification |
| State Tax | 8 | Multi-state sourcing, nexus |
| Retirement & Savings | 6 | 401k max, backdoor Roth |
| Year-End Planning | 7 | Charitable bunching, HSA deadline |
| Additional | 5 | Estimated payments, audit risk |

### 7.2 Alert Engine Implementation

```python
class AlertEngine:
    """Evaluate tax alerts based on user's financial data."""

    async def evaluate_all_alerts(
        self,
        user_id: str,
        financial_context: FinancialContext
    ) -> List[Alert]:
        """Run all alert rules against user's data."""

        alerts = []

        # Critical Underwithholding Check
        if result := self.check_underwithholding(financial_context):
            alerts.append(result)

        # AMT Alerts
        if result := self.check_amt_exposure(financial_context):
            alerts.append(result)

        # Capital Gains Alerts
        alerts.extend(self.check_capital_gains(financial_context))

        # ... all other categories

        # Sort by priority
        alerts.sort(key=lambda a: (a.priority.value, -a.impact_amount))

        return alerts

    def check_underwithholding(
        self,
        ctx: FinancialContext
    ) -> Optional[Alert]:
        """UW-001: Critical underwithholding alert."""

        gap = ctx.estimated_liability - ctx.ytd_withheld
        gap_pct = gap / ctx.estimated_liability if ctx.estimated_liability else 0

        if gap > 10000 and gap_pct > 0.15:
            return Alert(
                id="UW-001",
                category="UNDERWITHHOLDING",
                priority=AlertPriority.CRITICAL,
                title="Critical Underwithholding Detected",
                message=f"You're on track to owe ${gap:,.0f} at filing. "
                        f"Consider increasing withholding or making estimated payments.",
                impact_amount=gap,
                action_items=[
                    "Adjust W-4 to increase withholding",
                    f"Make Q4 estimated payment of ${gap/2:,.0f}",
                    "Review RSU sell-to-cover ratios",
                ],
            )
        return None

    def check_wa_capital_gains(
        self,
        ctx: FinancialContext
    ) -> Optional[Alert]:
        """CG-009: WA capital gains threshold breach."""

        if ctx.resident_state != "WA":
            return None

        threshold = 270_000
        exposure = ctx.ytd_realized_gains - threshold

        if exposure > 0:
            tax = exposure * Decimal("0.07")
            return Alert(
                id="CG-009",
                category="CAPITAL_GAINS",
                priority=AlertPriority.WARNING,
                title="WA Capital Gains Tax Triggered",
                message=f"Your gains exceed the ${threshold:,} threshold by ${exposure:,.0f}. "
                        f"Estimated WA tax: ${tax:,.0f}.",
                impact_amount=tax,
                action_items=[
                    "Consider deferring additional sales to next year",
                    "Harvest losses to offset gains",
                    "Review if any gains qualify for exemptions",
                ],
            )
        return None
```

### 7.3 Alert Notification Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                       ALERT NOTIFICATION FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  TRIGGER EVENTS                                                     │
│  ├── Nightly sync completes                                        │
│  ├── Document uploaded                                              │
│  ├── User runs what-if scenario                                    │
│  └── Manual refresh requested                                       │
│                                                                     │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │  Alert Engine   │ ──── Evaluate all 73 rules                    │
│  └────────┬────────┘                                               │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │  Deduplication  │ ──── Remove already-seen alerts               │
│  └────────┬────────┘                                               │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────┐      ┌─────────────────┐                      │
│  │   CRITICAL      │ ──▶  │  Push + In-App  │                      │
│  └─────────────────┘      └─────────────────┘                      │
│  ┌─────────────────┐      ┌─────────────────┐                      │
│  │   WARNING       │ ──▶  │    In-App       │                      │
│  └─────────────────┘      └─────────────────┘                      │
│  ┌─────────────────┐      ┌─────────────────┐                      │
│  │   INFO          │ ──▶  │  Dashboard      │                      │
│  └─────────────────┘      └─────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. What-If Scenario Engine

### 8.1 Scenario Categories (23 Total)

| Category | Count | Key Scenarios |
|----------|-------|---------------|
| Equity Compensation | 5 | RSU sale timing, ISO exercise amount |
| Income Timing | 4 | Bonus deferral, income acceleration |
| Investment | 5 | Tax-loss harvesting, rebalancing |
| State Tax | 3 | Relocation timing, remote work |
| Retirement | 3 | Roth conversion, 401k contribution |
| Year-End | 3 | Charitable giving, estimated payments |

### 8.2 Scenario Engine Implementation

```python
class WhatIfEngine:
    """Interactive scenario modeling engine."""

    async def run_scenario(
        self,
        scenario_type: str,
        base_context: FinancialContext,
        parameters: Dict[str, Any]
    ) -> ScenarioResult:
        """Execute a what-if scenario and return impact analysis."""

        # Clone base context
        modified_context = base_context.copy()

        # Apply scenario modifications
        scenario_handler = self.get_handler(scenario_type)
        modified_context = scenario_handler.apply(modified_context, parameters)

        # Calculate taxes for both scenarios
        base_taxes = self.tax_engine.calculate(base_context)
        modified_taxes = self.tax_engine.calculate(modified_context)

        # Calculate deltas
        return ScenarioResult(
            base_federal=base_taxes.federal,
            modified_federal=modified_taxes.federal,
            federal_delta=modified_taxes.federal - base_taxes.federal,
            base_state=base_taxes.state,
            modified_state=modified_taxes.state,
            state_delta=modified_taxes.state - base_taxes.state,
            total_delta=modified_taxes.total - base_taxes.total,
            breakdown=self._generate_breakdown(base_taxes, modified_taxes),
            recommendations=self._generate_recommendations(
                scenario_type, base_taxes, modified_taxes, parameters
            ),
        )


class RSUSaleTimingScenario(ScenarioHandler):
    """Model impact of RSU sale timing."""

    PARAMETERS = {
        "shares_to_sell": {"type": "int", "min": 1, "max": 10000},
        "sale_price": {"type": "decimal", "source": "current_market"},
        "sale_month": {"type": "month", "min": 1, "max": 12},
    }

    def apply(
        self,
        context: FinancialContext,
        params: Dict[str, Any]
    ) -> FinancialContext:
        """Apply RSU sale to context."""
        shares = params["shares_to_sell"]
        price = params["sale_price"]
        month = params["sale_month"]

        # Find matching lot
        lot = self.find_lot(context.rsu_holdings, shares)

        # Calculate gain
        gain = shares * (price - lot.vest_fmv)
        is_long_term = lot.is_long_term_by_month(month)

        # Modify context
        if is_long_term:
            context.ltcg += gain
        else:
            context.stcg += gain

        # Check WA threshold
        if context.resident_state == "WA":
            context.wa_cap_gains_exposure = max(
                0, context.total_gains - 270_000
            )

        return context
```

### 8.3 Interactive UI Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RSU SALE TIMING SCENARIO                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  How many shares to sell?                                          │
│  ├────────────●──────────────────────────────────────────────────┤ │
│  0           150                                              500   │
│                                                                     │
│  When to sell?                                                     │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐    │
│  │ Jan │ Feb │ Mar │ Apr │ May │ Jun │ Jul │ Aug │ Sep │ Oct │    │
│  │     │     │ ███ │     │     │     │     │     │     │     │    │
│  └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘    │
│                                                                     │
│  ═══════════════════════════════════════════════════════════════   │
│                                                                     │
│  CURRENT SCENARIO IMPACT                                           │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                                                               │ │
│  │  Selling 150 shares in March 2025                            │ │
│  │                                                               │ │
│  │  Proceeds:           $62,250   (150 × $415.00)               │ │
│  │  Cost Basis:         $45,000   (150 × $300.00 vest FMV)      │ │
│  │  Capital Gain:       $17,250   SHORT-TERM                    │ │
│  │                                                               │ │
│  │  ────────────────────────────────────────────────────────    │ │
│  │                                                               │ │
│  │  Federal Tax Impact:    +$5,692   (32.99% marginal rate)     │ │
│  │  WA Cap Gains Impact:   +$1,208   (7% on excess of $270K)    │ │
│  │  NIIT Impact:           +$656    (3.8%)                      │ │
│  │                                                               │ │
│  │  TOTAL TAX IMPACT:      +$7,556                              │ │
│  │  NET AFTER TAX:         $54,694                              │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  💡 OPTIMIZATION SUGGESTION                                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Wait until September to sell                                 │ │
│  │  ├── Gain becomes LONG-TERM (15% vs 32.99%)                  │ │
│  │  ├── Federal tax: $2,588 (saves $3,104)                      │ │
│  │  └── Net benefit: $2,448 (after state tax change)            │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [Compare Options]  [Save Scenario]  [Get AI Analysis]             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. Technical Architecture

### 9.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       TAXLENS ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     FLUTTER APP (Client)                     │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │   │
│  │  │Dashboard│  │Scenarios│  │ Alerts  │  │Documents│        │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │   │
│  │       │            │            │            │              │   │
│  │  ┌────┴────────────┴────────────┴────────────┴────┐        │   │
│  │  │              State Management (Riverpod)        │        │   │
│  │  └────────────────────────┬────────────────────────┘        │   │
│  │                           │                                  │   │
│  │  ┌────────────────────────┴────────────────────────┐        │   │
│  │  │              Local Cache (Drift/SQLite)          │        │   │
│  │  └────────────────────────┬────────────────────────┘        │   │
│  └───────────────────────────┼─────────────────────────────────┘   │
│                              │ HTTPS (TLS 1.3)                      │
│  ┌───────────────────────────┼─────────────────────────────────┐   │
│  │                     PYTHON BACKEND                           │   │
│  │                           │                                  │   │
│  │  ┌────────────────────────┴────────────────────────┐        │   │
│  │  │                 FastAPI Application              │        │   │
│  │  │  ┌─────────────────────────────────────────┐    │        │   │
│  │  │  │ /api/tax  /api/alerts  /api/scenarios   │    │        │   │
│  │  │  │ /api/documents  /api/advisor            │    │        │   │
│  │  │  └─────────────────────────────────────────┘    │        │   │
│  │  └─────────────────────────────────────────────────┘        │   │
│  │                           │                                  │   │
│  │  ┌────────────┬───────────┴────────────┬────────────┐       │   │
│  │  │            │                        │            │       │   │
│  │  ▼            ▼                        ▼            ▼       │   │
│  │  ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐          │   │
│  │  │  Tax   │  │ Alert  │  │ What-If  │  │  Doc   │          │   │
│  │  │ Engine │  │ Engine │  │  Engine  │  │Extract │          │   │
│  │  └────────┘  └────────┘  └──────────┘  └────────┘          │   │
│  │                           │                                  │   │
│  │  ┌────────────────────────┴────────────────────────┐        │   │
│  │  │              Database (SQLite → Supabase)        │        │   │
│  │  └─────────────────────────────────────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌───────────────────────────┼─────────────────────────────────┐   │
│  │                  EXTERNAL SERVICES                           │   │
│  │                           │                                  │   │
│  │  ┌────────────┬───────────┴───────────┬────────────┐        │   │
│  │  │            │                       │            │        │   │
│  │  ▼            ▼                       ▼            ▼        │   │
│  │  ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐          │   │
│  │  │ Plaid  │  │ Claude │  │ Supabase │  │ Sentry │          │   │
│  │  │  API   │  │  API   │  │  (opt)   │  │ (opt)  │          │   │
│  │  └────────┘  └────────┘  └──────────┘  └────────┘          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Mobile** | Flutter 3.x | Single codebase for iOS, Android, Web |
| **State** | Riverpod | Type-safe, testable state management |
| **Local DB** | Drift (SQLite) | Offline-first, familiar SQL |
| **Backend** | FastAPI (Python) | Fast, modern, auto-docs |
| **Database** | SQLite → Supabase | Easy migration path |
| **Doc AI** | Claude API | Best-in-class document understanding |
| **Aggregation** | Plaid | Industry standard for financial data |
| **Hosting** | Render | Simple, good free tier |

### 9.3 Database Schema

```sql
-- Core User Data
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filing_status TEXT DEFAULT 'single',
    resident_state TEXT DEFAULT 'CA',
    spouse_works BOOLEAN DEFAULT FALSE
);

-- Plaid Connections
CREATE TABLE plaid_items (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    access_token TEXT NOT NULL,  -- Encrypted
    institution_id TEXT,
    institution_name TEXT,
    last_sync TIMESTAMP
);

-- Investment Holdings
CREATE TABLE holdings (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    plaid_item_id TEXT REFERENCES plaid_items(id),
    symbol TEXT NOT NULL,
    name TEXT,
    quantity DECIMAL(18,8),
    price DECIMAL(18,4),
    value DECIMAL(18,2),
    cost_basis DECIMAL(18,2),
    security_type TEXT,
    as_of_date DATE
);

-- Equity Grants
CREATE TABLE equity_grants (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    grant_type TEXT NOT NULL,  -- RSU, ISO, NSO, ESPP
    company TEXT NOT NULL,
    symbol TEXT,
    grant_date DATE NOT NULL,
    shares_granted INTEGER,
    exercise_price DECIMAL(18,4),  -- For options
    vesting_schedule JSONB
);

-- Tax Documents
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    document_type TEXT NOT NULL,
    tax_year INTEGER,
    file_path TEXT,
    extracted_data JSONB,
    extraction_status TEXT DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts
CREATE TABLE alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    alert_code TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    title TEXT,
    message TEXT,
    impact_amount DECIMAL(18,2),
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMP
);

-- What-If Scenarios (Saved)
CREATE TABLE saved_scenarios (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    scenario_type TEXT NOT NULL,
    name TEXT,
    parameters JSONB,
    result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9.4 API Endpoints

```yaml
# Tax Calculations
GET  /api/tax/estimate           # Current year estimate
GET  /api/tax/breakdown          # Detailed breakdown
GET  /api/tax/withholding-gap    # YTD withholding vs liability

# Alerts
GET  /api/alerts                 # All active alerts
GET  /api/alerts/{id}            # Single alert details
POST /api/alerts/{id}/dismiss    # Dismiss alert

# What-If Scenarios
GET  /api/scenarios/types        # Available scenario types
POST /api/scenarios/run          # Execute scenario
GET  /api/scenarios/saved        # User's saved scenarios
POST /api/scenarios/save         # Save a scenario

# Documents
POST /api/documents/upload       # Upload document
GET  /api/documents              # List documents
GET  /api/documents/{id}         # Document details + extracted data
DELETE /api/documents/{id}       # Delete document

# Holdings & Accounts
GET  /api/holdings               # Current holdings
GET  /api/holdings/lots          # Tax lot details
GET  /api/accounts               # Connected accounts
POST /api/accounts/sync          # Force sync

# AI Advisor
GET  /api/advisor/recommendations  # AI tax recommendations
POST /api/advisor/analyze          # Analyze specific situation
```

### 9.5 Performance Targets

| Operation | Target | Implementation |
|-----------|--------|----------------|
| Tax calculation | <100ms | Pre-computed brackets, caching |
| Alert evaluation | <500ms | Parallel rule evaluation |
| Scenario modeling | <200ms | Incremental recalculation |
| Document extraction | <10s | Claude API streaming |
| Plaid sync | <5s | Background job with incremental updates |

---

## 10. Privacy & Security Framework

### 10.1 Data Protection

| Measure | Implementation |
|---------|----------------|
| **Encryption at Rest** | SQLCipher (AES-256) for local DB |
| **Encryption in Transit** | TLS 1.3 with certificate pinning |
| **Key Storage** | iOS Keychain / Android Keystore |
| **Field Encryption** | SSN, account numbers encrypted |

### 10.2 Authentication

```python
AUTH_CONFIG = {
    "primary_methods": [
        "email_password",
        "sign_in_with_apple",
        "google_oauth",
    ],
    "password_requirements": {
        "min_length": 12,
        "require_mixed_case": True,
        "require_numbers": True,
        "check_breach_database": True,
    },
    "session": {
        "access_token_lifetime": "15m",
        "refresh_token_lifetime": "30d",
        "idle_timeout": "5m",
    },
    "sensitive_ops_require": "biometric_or_pin",
}
```

### 10.3 Consent Framework

| Feature | Consent Required | Default |
|---------|-----------------|---------|
| Core tax calculations | Implied (required) | Enabled |
| Plaid bank connection | Explicit opt-in | Disabled |
| AI document extraction | Explicit opt-in | Disabled |
| AI recommendations | Explicit opt-in | Disabled |
| Cloud backup | Explicit opt-in | Disabled |

### 10.4 Compliance

| Regulation | Requirements Met |
|------------|-----------------|
| **CCPA** | Right to access, delete, portability |
| **GLBA** | Privacy notice, data safeguards |
| **SOC 2** | Planned for production |

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

```
DELIVERABLES:
├── Project setup (Flutter + FastAPI)
├── Database schema implementation
├── Core tax calculation engine
│   ├── Federal brackets (2025)
│   ├── FICA calculations
│   ├── Standard deductions
│   └── Basic capital gains
├── Plaid integration (basic)
│   ├── Account linking
│   └── Holdings sync
└── Basic Flutter app
    ├── Authentication
    ├── Dashboard (net worth)
    └── Holdings list

EFFORT: 80-120 hours
```

### Phase 2: Equity Intelligence (Weeks 5-8)

```
DELIVERABLES:
├── RSU tax calculations
│   ├── Vest withholding
│   ├── Sale capital gains
│   └── Multi-lot tracking
├── ISO/NSO calculations
│   ├── Exercise tax impact
│   ├── AMT calculations
│   └── Qualifying disposition logic
├── ESPP calculations
├── State tax engine (CA, NY, WA)
├── Multi-state RSU sourcing
└── Tax estimate dashboard

EFFORT: 100-140 hours
```

### Phase 3: Alerts & Scenarios (Weeks 9-12)

```
DELIVERABLES:
├── Alert engine
│   ├── 73 alert rules
│   ├── Priority system
│   └── Notification delivery
├── What-if scenario engine
│   ├── 23 scenario types
│   ├── Interactive sliders
│   └── Side-by-side comparison
├── Document intelligence
│   ├── Claude Vision integration
│   ├── W-2, 1099-B extraction
│   └── Validation UI
└── AI recommendations

EFFORT: 120-160 hours
```

### Phase 4: Polish & Launch (Weeks 13-16)

```
DELIVERABLES:
├── Offline mode
├── Performance optimization
├── Security audit
├── Privacy compliance
├── App store submission
└── Production deployment

EFFORT: 80-100 hours
```

### Total Estimated Effort

| Phase | Hours | Cumulative |
|-------|-------|------------|
| Phase 1: Foundation | 80-120 | 80-120 |
| Phase 2: Equity | 100-140 | 180-260 |
| Phase 3: Alerts/Scenarios | 120-160 | 300-420 |
| Phase 4: Polish | 80-100 | 380-520 |

**Total: 380-520 hours (~10-13 weeks at 40 hrs/week)**

---

## 12. Appendices

### Appendix A: Complete Alert Catalog

See [Task 6: Red Flag Dashboard](./task6_red_flag_dashboard.md) for the complete list of 73 alerts with trigger conditions, messages, and action items.

### Appendix B: What-If Scenario Details

See [Task 7: What-If Sliders](./task7_what_if_sliders.md) for detailed specifications of all 23 scenario types.

### Appendix C: State Tax Brackets

See [Task 4: State Tax Calculations](./task4_state_tax_calculations.md) for complete 2025 bracket tables for CA, NY, and WA.

### Appendix D: Document Extraction Schemas

See [Task 5: Data Mapping & Integration](./task5_data_mapping_integration.md) for Claude Vision extraction schemas.

### Appendix E: Technical Implementation Details

See [Task 8: Technical Implementation](./task8_technical_implementation.md) for detailed API schemas, database design, and architecture diagrams.

### Appendix F: Security & Privacy Framework

See [Task 9: User Trust & Data Sensitivity](./task9_user_trust_data_sensitivity.md) for comprehensive security architecture and compliance requirements.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial specification |

---

## Next Steps

1. **Technical Review:** Validate architecture with senior engineers
2. **User Research:** Interview 10-15 target users for feedback
3. **Prioritization:** Finalize MVP feature set for Phase 1-2
4. **Team Formation:** Identify required skills (Flutter, Python, Tax)
5. **Development Kickoff:** Sprint 0 setup and planning
