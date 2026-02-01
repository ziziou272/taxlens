# Task 5: Data Mapping & Integration - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document specifies data mapping between external sources (Plaid, document OCR, equity platforms) and internal TaxLens tax models. Key findings:

1. **Plaid provides ~70% of needed data** - Holdings, transactions, cost basis available
2. **Critical gaps require manual input** - RSU grants, ISO exercise history, vesting schedules
3. **Document OCR can fill gaps** - W-2, 1099-B, brokerage statements parsed via Claude Vision
4. **Equity platforms have limited APIs** - E*TRADE EEO, Morgan Stanley Shareworks have REST APIs but require corporate relationships

---

## 1. Data Sources Overview

### 1.1 Primary Data Sources

| Source | Data Type | Access Method | Reliability |
|--------|-----------|---------------|-------------|
| **Plaid Investments** | Holdings, transactions, cost basis | REST API | High (real-time) |
| **Document OCR (Claude)** | W-2, 1099-B/DIV/INT, pay stubs | Vision API | High (97%+ accuracy) |
| **Manual Input** | RSU/ISO grants, vesting schedules | User entry | Depends on user |
| **Equity Platforms** | Grant details, exercise history | REST API (limited) | High (if accessible) |

### 1.2 Data Coverage Matrix

| Data Needed | Plaid | Document OCR | Manual | Equity Platform |
|-------------|-------|--------------|--------|-----------------|
| Bank account balances | **YES** | - | - | - |
| Investment holdings | **YES** | - | - | - |
| Cost basis | Partial | **YES** (1099-B) | Backup | **YES** |
| W-2 income | - | **YES** | Backup | - |
| RSU grant details | - | - | **YES** | **YES** |
| RSU vesting schedule | - | - | **YES** | **YES** |
| ISO/NSO grant details | - | - | **YES** | **YES** |
| ESPP purchase history | - | **YES** (3922) | Backup | **YES** |
| Dividend income | - | **YES** (1099-DIV) | - | - |
| Capital gains/losses | - | **YES** (1099-B) | - | - |
| Federal withholding | - | **YES** (W-2) | Backup | - |
| State residence history | - | - | **YES** | - |

---

## 2. Plaid Investment API

### 2.1 Available Endpoints

| Endpoint | Purpose | Data Returned |
|----------|---------|---------------|
| `/investments/holdings/get` | Current holdings | Securities, positions, values |
| `/investments/transactions/get` | Transaction history | Buy/sell, dividends (24 months) |
| `/accounts/get` | Account info | Account types, balances |

### 2.2 Holdings Data Schema

```json
{
  "holdings": [
    {
      "account_id": "k67E4xKvMlhmleEa4pg9hlwGGNnnEeixPolGm",
      "security_id": "NDVQrXQoqzt5v3bAe8qRt4A7mK7wvZCLEBBJk",
      "cost_basis": 10.00,
      "quantity": 2.0,
      "institution_price": 10.42,
      "institution_price_as_of": "2025-01-15",
      "institution_value": 20.84,
      "iso_currency_code": "USD",
      "vested_quantity": null,
      "vested_value": null
    }
  ],
  "securities": [
    {
      "security_id": "NDVQrXQoqzt5v3bAe8qRt4A7mK7wvZCLEBBJk",
      "name": "Microsoft Corporation",
      "ticker_symbol": "MSFT",
      "type": "equity",
      "cusip": "594918104",
      "isin": "US5949181045",
      "is_cash_equivalent": false
    }
  ]
}
```

### 2.3 Investment Transaction Types

| Transaction Type | Description | Tax Relevance |
|------------------|-------------|---------------|
| `buy` | Purchase of security | Cost basis tracking |
| `sell` | Sale of security | Capital gains calculation |
| `dividend` | Cash dividend | Dividend income (1099-DIV) |
| `capital_gains_long` | Long-term capital gain distribution | LTCG treatment |
| `capital_gains_short` | Short-term capital gain distribution | STCG treatment |
| `cash` | Cash transfer | N/A |
| `contribution` | Account contribution | N/A |
| `fee` | Account fees | Potentially deductible |
| `interest` | Interest earned | Interest income (1099-INT) |
| `transfer` | Security transfer | Basis tracking |

### 2.4 Plaid Data Gaps

| Missing Data | Impact | Workaround |
|--------------|--------|------------|
| RSU grant details | Cannot calculate underwithholding | Manual input |
| ISO/NSO exercise history | Cannot calculate AMT | Manual input |
| Vesting schedules | Cannot project future income | Manual input |
| Cost basis (some institutions) | May show $0 | Document OCR (1099-B) |
| Tax lot details | Incorrect gain/loss | Manual input or OCR |

### 2.5 Plaid to TaxLens Mapping

```python
class PlaidHoldingMapper:
    """Map Plaid holdings to TaxLens internal model."""

    def map_holding(self, plaid_holding: dict, security: dict) -> Holding:
        return Holding(
            account_id=plaid_holding['account_id'],
            security_id=plaid_holding['security_id'],
            ticker=security.get('ticker_symbol'),
            name=security.get('name'),
            security_type=self._map_security_type(security.get('type')),
            quantity=Decimal(str(plaid_holding['quantity'])),
            cost_basis=Decimal(str(plaid_holding.get('cost_basis', 0))),
            current_price=Decimal(str(plaid_holding['institution_price'])),
            current_value=Decimal(str(plaid_holding['institution_value'])),
            price_as_of=parse_date(plaid_holding.get('institution_price_as_of')),
            unrealized_gain=self._calculate_unrealized_gain(plaid_holding),
            cusip=security.get('cusip'),
            isin=security.get('isin'),
        )

    def _map_security_type(self, plaid_type: str) -> SecurityType:
        mapping = {
            'equity': SecurityType.STOCK,
            'etf': SecurityType.ETF,
            'mutual fund': SecurityType.MUTUAL_FUND,
            'cash': SecurityType.CASH,
            'derivative': SecurityType.OPTION,
            'cryptocurrency': SecurityType.CRYPTO,
        }
        return mapping.get(plaid_type, SecurityType.OTHER)

    def _calculate_unrealized_gain(self, holding: dict) -> Decimal:
        value = Decimal(str(holding['institution_value']))
        basis = Decimal(str(holding.get('cost_basis', 0)))
        if basis == 0:
            return Decimal('0')  # Unknown basis
        return value - (basis * Decimal(str(holding['quantity'])))
```

---

## 3. Document Intelligence (Claude Vision)

### 3.1 Supported Document Types

| Document | Key Fields Extracted | Accuracy |
|----------|---------------------|----------|
| **W-2** | Wages, withholding, Box 12 codes | 97%+ |
| **1099-B** | Proceeds, cost basis, gain/loss, dates | 95%+ |
| **1099-DIV** | Ordinary/qualified dividends, cap gains | 97%+ |
| **1099-INT** | Interest income, tax-exempt | 97%+ |
| **Form 3921** | ISO exercise details | 95%+ |
| **Form 3922** | ESPP purchase details | 95%+ |
| **Pay Stub** | YTD income, withholding, deductions | 90%+ |
| **Brokerage Statement** | Holdings, transactions, basis | 90%+ |

### 3.2 W-2 Extraction Schema

```python
class W2Data(BaseModel):
    """Extracted W-2 data from Claude Vision."""

    document_type: Literal["W-2"] = "W-2"
    tax_year: int
    employer_name: str
    employer_ein: str  # XX-XXXXXXX format
    employer_address: Optional[str]

    # Box 1-6: Income and Withholding
    wages_tips_compensation: Decimal  # Box 1
    federal_income_tax_withheld: Decimal  # Box 2
    social_security_wages: Decimal  # Box 3
    social_security_tax_withheld: Decimal  # Box 4
    medicare_wages: Decimal  # Box 5
    medicare_tax_withheld: Decimal  # Box 6

    # Box 7-14: Additional Info
    social_security_tips: Optional[Decimal]  # Box 7
    allocated_tips: Optional[Decimal]  # Box 8
    dependent_care_benefits: Optional[Decimal]  # Box 10
    nonqualified_plans: Optional[Decimal]  # Box 11
    box_12_codes: List[Box12Entry]  # Box 12a-d
    statutory_employee: bool = False  # Box 13
    retirement_plan: bool = False  # Box 13
    third_party_sick_pay: bool = False  # Box 13
    box_14_other: List[Box14Entry]  # Box 14

    # Box 15-20: State/Local
    state: Optional[str]  # Box 15
    state_employer_id: Optional[str]  # Box 15
    state_wages: Optional[Decimal]  # Box 16
    state_income_tax_withheld: Optional[Decimal]  # Box 17
    local_wages: Optional[Decimal]  # Box 18
    local_income_tax_withheld: Optional[Decimal]  # Box 19
    locality_name: Optional[str]  # Box 20


class Box12Entry(BaseModel):
    code: str  # D, E, W, DD, etc.
    amount: Decimal


class Box14Entry(BaseModel):
    description: str
    amount: Decimal
```

### 3.3 1099-B Extraction Schema

```python
class Form1099B(BaseModel):
    """Extracted 1099-B data from Claude Vision."""

    document_type: Literal["1099-B"] = "1099-B"
    tax_year: int
    payer_name: str  # Broker/institution
    payer_tin: str

    transactions: List[BrokerageTransaction]
    total_proceeds: Decimal
    total_cost_basis: Optional[Decimal]
    total_wash_sale_adjustments: Optional[Decimal]


class BrokerageTransaction(BaseModel):
    """Single sale transaction from 1099-B."""

    description: str  # Security name
    quantity: Optional[Decimal]
    date_acquired: Optional[date]
    date_sold: date
    proceeds: Decimal  # Box 1d
    cost_basis: Optional[Decimal]  # Box 1e
    accrued_market_discount: Optional[Decimal]  # Box 1f
    wash_sale_loss_disallowed: Optional[Decimal]  # Box 1g
    gain_loss: Optional[Decimal]

    # Classification
    term: Literal["short", "long", "unknown"]
    basis_reported_to_irs: bool  # Box 12
    noncovered_security: bool  # Box 5
    loss_not_allowed_based_on_amount: bool  # Box 6
    ordinary_gain_loss: bool  # Box 2

    # Adjustments
    form_8949_box: Optional[str]  # A, B, C, D, E, F
    adjustment_code: Optional[str]  # W for wash sale, etc.
```

### 3.4 Form 3921 (ISO Exercise) Schema

```python
class Form3921(BaseModel):
    """ISO exercise information from Form 3921."""

    document_type: Literal["3921"] = "3921"
    tax_year: int
    corporation_name: str
    corporation_ein: str

    # Box 1-8
    date_granted: date  # Box 1
    date_exercised: date  # Box 2
    exercise_price_per_share: Decimal  # Box 3
    fmv_per_share_on_exercise: Decimal  # Box 4
    shares_transferred: int  # Box 5
    # Boxes 6-8 for transfer, if applicable


class Form3922(BaseModel):
    """ESPP purchase information from Form 3922."""

    document_type: Literal["3922"] = "3922"
    tax_year: int
    corporation_name: str
    corporation_ein: str

    # Box 1-9
    date_granted: date  # Box 1 (offering date)
    date_transferred: date  # Box 2 (purchase date)
    fmv_on_grant_date: Decimal  # Box 3
    fmv_on_transfer_date: Decimal  # Box 4
    exercise_price_per_share: Decimal  # Box 5
    shares_transferred: int  # Box 6
```

### 3.5 Claude Vision Integration

```python
import anthropic
import base64
from pathlib import Path

async def extract_tax_document(
    pdf_path: Path,
    document_type: str = None
) -> dict:
    """
    Extract structured data from tax document using Claude Vision.

    Args:
        pdf_path: Path to PDF file
        document_type: Optional hint (W-2, 1099-B, etc.)

    Returns:
        Structured extraction result
    """
    client = anthropic.Anthropic()

    # Read PDF as base64
    pdf_data = base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")

    # Build prompt
    prompt = build_extraction_prompt(document_type)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    # Parse JSON response
    return parse_extraction_response(response.content[0].text, document_type)


def build_extraction_prompt(document_type: str = None) -> str:
    """Build extraction prompt for tax document."""

    base_prompt = """
    Analyze this tax document and extract all relevant data into a structured JSON format.

    First, identify the document type (W-2, 1099-B, 1099-DIV, 1099-INT, 3921, 3922, etc.).

    Then extract all fields according to the appropriate schema:

    For W-2:
    - All numbered boxes (1-20)
    - Employer information
    - Box 12 codes with amounts
    - Box 14 descriptions with amounts

    For 1099-B:
    - Each transaction with dates, proceeds, cost basis
    - Wash sale adjustments
    - Long-term vs short-term classification

    For 1099-DIV:
    - Ordinary dividends (Box 1a)
    - Qualified dividends (Box 1b)
    - Capital gains distributions (Box 2a)
    - Foreign taxes paid (Box 7)

    Return a valid JSON object with all extracted fields.
    Use null for fields that are not present or not applicable.
    Use string format for currency amounts to preserve precision.
    """

    if document_type:
        base_prompt += f"\n\nThis document is expected to be a {document_type}."

    return base_prompt
```

---

## 4. Manual Input Requirements

### 4.1 Required Manual Data

| Data Category | Fields | Why Needed |
|--------------|--------|------------|
| **User Profile** | Filing status, state residence, dependents | Tax calculation basis |
| **RSU Grants** | Grant date, shares, vesting schedule, employer | Underwithholding, multi-state |
| **ISO Grants** | Grant date, strike price, shares, expiration | AMT calculation |
| **NSO Grants** | Grant date, strike price, shares, expiration | Exercise planning |
| **ESPP** | Offering date, purchase date, discount % | Disposition type |
| **State History** | States lived, dates, work days | Multi-state sourcing |
| **Prior Year Data** | AMT credit carryforward, loss carryforward | Current year calculation |

### 4.2 RSU Grant Input Schema

```python
class RSUGrantInput(BaseModel):
    """User-provided RSU grant information."""

    grant_id: Optional[str]  # User can provide or auto-generate
    employer: str
    ticker_symbol: str
    grant_date: date
    total_shares: int
    vesting_schedule: VestingSchedule

    # Populated on vest
    vested_shares: int = 0
    vest_events: List[VestEvent] = []


class VestingSchedule(BaseModel):
    """RSU vesting schedule."""

    schedule_type: Literal["cliff", "monthly", "quarterly", "annual", "custom"]
    cliff_months: Optional[int]  # For cliff vesting
    total_vesting_months: int  # Total vesting period
    vest_events: Optional[List[ScheduledVest]]  # For custom schedules


class ScheduledVest(BaseModel):
    vest_date: date
    shares: int


class VestEvent(BaseModel):
    """Actual vest event (historical or projected)."""

    vest_date: date
    shares_vested: int
    fmv_at_vest: Optional[Decimal]
    withheld_shares: Optional[int]
    net_shares: Optional[int]
    state_worked_in: str  # For multi-state sourcing
```

### 4.3 ISO Grant Input Schema

```python
class ISOGrantInput(BaseModel):
    """User-provided ISO grant information."""

    grant_id: Optional[str]
    employer: str
    ticker_symbol: str
    grant_date: date
    expiration_date: date
    total_shares: int
    strike_price: Decimal
    vesting_schedule: VestingSchedule

    # Updated over time
    exercised_shares: int = 0
    exercise_events: List[ISOExerciseEvent] = []


class ISOExerciseEvent(BaseModel):
    """ISO exercise event."""

    exercise_date: date
    shares_exercised: int
    fmv_at_exercise: Decimal
    strike_price: Decimal
    bargain_element: Decimal  # Computed
    shares_held: int  # Shares still held
    shares_sold: int  # Shares sold same day or later
    sale_events: List[ISOSaleEvent] = []


class ISOSaleEvent(BaseModel):
    """Sale of ISO shares."""

    sale_date: date
    shares_sold: int
    sale_price: Decimal
    disposition_type: Literal["qualifying", "disqualifying"]
    ordinary_income: Decimal  # Disqualifying only
    capital_gain: Decimal
```

---

## 5. Data Validation Rules

### 5.1 Cross-Source Validation

```python
class DataValidator:
    """Validate data consistency across sources."""

    def validate_w2_income(
        self,
        w2_data: W2Data,
        pay_stubs: List[PayStub],
        plaid_transactions: List[Transaction]
    ) -> ValidationResult:
        """
        Validate W-2 income against pay stubs and bank transactions.
        """
        issues = []

        # Check W-2 wages vs pay stub YTD
        if pay_stubs:
            last_stub = max(pay_stubs, key=lambda s: s.pay_date)
            if abs(w2_data.wages_tips_compensation - last_stub.ytd_gross) > 100:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="wages",
                    message=f"W-2 wages ({w2_data.wages_tips_compensation}) "
                            f"differs from YTD pay stub ({last_stub.ytd_gross})"
                ))

        # Check deposits match income pattern
        if plaid_transactions:
            payroll_deposits = self._identify_payroll_deposits(plaid_transactions)
            expected_deposits = w2_data.wages_tips_compensation / 26  # Biweekly
            if not self._deposits_match_income(payroll_deposits, expected_deposits):
                issues.append(ValidationIssue(
                    severity="info",
                    field="deposits",
                    message="Bank deposits don't clearly match W-2 income pattern"
                ))

        return ValidationResult(issues=issues)

    def validate_cost_basis(
        self,
        plaid_holdings: List[Holding],
        form_1099b: Form1099B
    ) -> ValidationResult:
        """
        Validate Plaid cost basis against 1099-B.
        """
        issues = []

        for holding in plaid_holdings:
            if holding.cost_basis == 0:
                issues.append(ValidationIssue(
                    severity="warning",
                    field=f"cost_basis_{holding.ticker}",
                    message=f"Missing cost basis for {holding.ticker}. "
                            f"Check 1099-B or enter manually."
                ))

        return ValidationResult(issues=issues)

    def validate_rsu_data(
        self,
        rsu_grants: List[RSUGrantInput],
        w2_data: W2Data,
        form_1099b: Optional[Form1099B]
    ) -> ValidationResult:
        """
        Validate RSU grants against W-2 and 1099-B.
        """
        issues = []

        # Check if RSU income is reflected in W-2
        total_rsu_income = sum(
            vest.fmv_at_vest * vest.shares_vested
            for grant in rsu_grants
            for vest in grant.vest_events
            if vest.fmv_at_vest
        )

        # RSU income should be included in W-2 Box 1
        if total_rsu_income > 0 and w2_data.wages_tips_compensation < total_rsu_income:
            issues.append(ValidationIssue(
                severity="error",
                field="rsu_income",
                message=f"RSU income ({total_rsu_income}) exceeds W-2 wages. "
                        f"Verify RSU data or check if income spans multiple W-2s."
            ))

        return ValidationResult(issues=issues)
```

### 5.2 Data Completeness Check

```python
def check_data_completeness(user_data: UserFinancialData) -> CompletenessReport:
    """
    Check if we have all required data for tax calculations.
    """
    requirements = []

    # Basic requirements
    if not user_data.filing_status:
        requirements.append(Requirement(
            field="filing_status",
            priority="required",
            message="Filing status needed for tax bracket calculation"
        ))

    if not user_data.state_of_residence:
        requirements.append(Requirement(
            field="state_of_residence",
            priority="required",
            message="State of residence needed for state tax calculation"
        ))

    # Income requirements
    if not user_data.w2_data and not user_data.estimated_income:
        requirements.append(Requirement(
            field="income",
            priority="required",
            message="Upload W-2 or enter estimated income"
        ))

    # Equity requirements (if user has equity comp)
    if user_data.has_equity_compensation:
        if not user_data.rsu_grants:
            requirements.append(Requirement(
                field="rsu_grants",
                priority="recommended",
                message="RSU grant details improve underwithholding prediction"
            ))

        if not user_data.state_work_history:
            requirements.append(Requirement(
                field="state_work_history",
                priority="recommended",
                message="State work history needed for multi-state RSU sourcing"
            ))

    # Capital gains requirements
    if user_data.has_investments and not user_data.form_1099b:
        requirements.append(Requirement(
            field="form_1099b",
            priority="recommended",
            message="1099-B improves capital gains accuracy"
        ))

    return CompletenessReport(
        complete=all(r.priority != "required" for r in requirements),
        requirements=requirements
    )
```

---

## 6. Equity Platform Integration

### 6.1 E*TRADE Equity Edge Online API

| Endpoint | Data Available | Access |
|----------|----------------|--------|
| `/participants` | Employee participant data | Corporate client only |
| `/grants` | Grant details, vesting schedules | Corporate client only |
| `/transactions` | Exercise, sell, vest transactions | Corporate client only |
| `/payroll` | Tax withholding data | Corporate client only |

**Limitation:** API access requires corporate relationship with E*TRADE. Individual participants cannot access programmatically.

### 6.2 Morgan Stanley Shareworks

| Feature | Availability |
|---------|--------------|
| API Access | Corporate clients via data feeds |
| HRIS Integration | Real-time via REST API |
| Participant Portal | Web-only, no API for individuals |

### 6.3 Fidelity Stock Plan Services

| Feature | Availability |
|---------|--------------|
| Integration Xchange | For advisors/institutions only |
| Participant Data | Export via web portal (CSV) |
| API Access | Not available for individuals |

### 6.4 Workaround: Document Upload

Since equity platform APIs are not available to individuals, TaxLens should:

1. **Document Upload** - Accept PDF exports from equity portals
2. **Form 3921/3922 Parsing** - Extract ISO/ESPP data from tax forms
3. **Manual Entry** - Guided input for grant details
4. **CSV Import** - Accept exported transaction history

---

## 7. Data Flow Architecture

### 7.1 Integration Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │   Plaid     │  │   Claude    │  │   Manual    │  │   CSV     │  │
│  │ Investments │  │   Vision    │  │   Input     │  │  Import   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │
│         │                │                │                │        │
└─────────┼────────────────┼────────────────┼────────────────┼────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA NORMALIZATION LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      Data Mappers                               ││
│  │  - PlaidHoldingMapper                                           ││
│  │  - W2Mapper                                                     ││
│  │  - Form1099BMapper                                              ││
│  │  - RSUGrantMapper                                               ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      Validators                                 ││
│  │  - CrossSourceValidator                                         ││
│  │  - CompletenessChecker                                          ││
│  │  - RedFlagDetector                                              ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     TAXLENS DATA MODEL                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │   Income    │  │  Holdings   │  │   Equity    │  │   Tax     │  │
│  │   Sources   │  │  Portfolio  │  │   Grants    │  │  Context  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Data Refresh Strategy

| Data Type | Refresh Frequency | Trigger |
|-----------|-------------------|---------|
| Bank balances | Daily | Automatic (Plaid webhook) |
| Investment holdings | Daily | Automatic (Plaid webhook) |
| Investment transactions | Daily | Automatic (Plaid webhook) |
| Tax documents (W-2, 1099) | On upload | User action |
| RSU/ISO grants | On change | User action |
| Tax calculations | On data change | Automatic |

---

## 8. API Cost Estimation

### 8.1 Plaid Pricing

| Item | Cost | Notes |
|------|------|-------|
| Per connection | $0.50-$2.00 | Volume discounts available |
| Investment data | Included | With base connection |
| Daily refresh | Included | No additional cost |

**Estimated cost per user:** $1-3/year

### 8.2 Claude API Pricing

| Document Type | Tokens (est.) | Cost per doc |
|--------------|---------------|--------------|
| W-2 (1 page) | ~2,000 | ~$0.006 |
| 1099-B (3 pages) | ~5,000 | ~$0.015 |
| Pay Stub (2 pages) | ~3,000 | ~$0.009 |
| Brokerage Statement | ~10,000 | ~$0.030 |

**Estimated cost per user:** $1-3/year (assuming ~50-100 documents)

---

## 9. Sources

### Plaid Documentation
- https://plaid.com/docs/investments/
- https://plaid.com/docs/api/products/investments/

### Document AI
- Azure Document Intelligence: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/
- Google Document AI: https://cloud.google.com/document-ai

### Equity Platforms
- E*TRADE Equity Edge Online API: https://developer.etrade.com/corporate-services
- Morgan Stanley Shareworks: https://www.morganstanley.com/atwork/shareworks

---

*Document generated as part of TaxLens Phase 1 Research*
