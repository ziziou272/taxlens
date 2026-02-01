# Task 8: Technical Implementation - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document specifies the technical architecture, API design, database schema, and performance requirements for TaxLens. Key decisions:

1. **Backend:** Python + FastAPI for tax calculations and API
2. **Frontend:** Flutter for cross-platform mobile/web
3. **Database:** SQLite (local) → Supabase (cloud)
4. **AI Integration:** Claude API for explanations and document OCR
5. **Data Aggregation:** Plaid for financial data
6. **Hosting:** Render for backend, Supabase for database

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐         │
│  │    iOS App    │   │  Android App  │   │    Web App    │         │
│  │   (Flutter)   │   │   (Flutter)   │   │   (Flutter)   │         │
│  └───────┬───────┘   └───────┬───────┘   └───────┬───────┘         │
│          │                   │                   │                  │
│          └───────────────────┼───────────────────┘                  │
│                              │                                      │
│                    ┌─────────▼─────────┐                            │
│                    │   Local Cache     │                            │
│                    │   (Drift/SQLite)  │                            │
│                    └─────────┬─────────┘                            │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER                                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    FastAPI Backend                              ││
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       ││
│  │  │ /accounts │ │   /tax    │ │ /portfolio│ │ /documents│       ││
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘       ││
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       ││
│  │  │ /advisor  │ │  /alerts  │ │ /what-if  │ │   /sync   │       ││
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘       ││
│  └─────────────────────────────────────────────────────────────────┘│
└──────────────────────────────┼──────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────┐
│                        SERVICE LAYER                                 │
├──────────────────────────────┼──────────────────────────────────────┤
│                              │                                       │
│  ┌─────────────┐  ┌──────────▼─────────┐  ┌─────────────┐           │
│  │   Plaid     │  │    Tax Engine      │  │   Claude    │           │
│  │   Client    │  │  (Calculations)    │  │    API      │           │
│  └──────┬──────┘  └────────────────────┘  └──────┬──────┘           │
│         │                                        │                   │
│         │         ┌────────────────────┐         │                   │
│         │         │   Alert Engine     │         │                   │
│         │         └────────────────────┘         │                   │
│         │                                        │                   │
│         │         ┌────────────────────┐         │                   │
│         │         │  What-If Engine    │         │                   │
│         │         └────────────────────┘         │                   │
│         │                                        │                   │
└─────────┼────────────────────────────────────────┼───────────────────┘
          │                                        │
          ▼                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │              SQLite (Local) / Supabase (Cloud)                  ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           ││
│  │  │ accounts │ │ holdings │ │ documents│ │ tax_data │           ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           ││
│  │  │  grants  │ │  alerts  │ │  cache   │ │   users  │           ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Flutter App** | UI, local caching, offline support |
| **FastAPI Backend** | Business logic, calculations, API |
| **Tax Engine** | Federal/state tax calculations |
| **Alert Engine** | Red flag detection and notifications |
| **What-If Engine** | Scenario modeling calculations |
| **Plaid Client** | Financial data aggregation |
| **Claude API** | Document OCR, explanations, advice |
| **Database** | Persistent storage, caching |

---

## 2. Technology Stack

### 2.1 Backend

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Language** | Python 3.11+ | Tax calculation libraries, AI integration |
| **Framework** | FastAPI | Async, auto-docs, type hints |
| **Database** | SQLite → PostgreSQL | Simple local → scalable cloud |
| **ORM** | SQLAlchemy 2.0 | Async support, type safety |
| **Validation** | Pydantic v2 | Request/response validation |
| **Task Queue** | Celery (optional) | Background sync jobs |
| **Caching** | Redis (cloud) | API response caching |

### 2.2 Frontend

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Framework** | Flutter 3.x | Single codebase, native performance |
| **State** | Riverpod | Clean, testable state management |
| **HTTP** | Dio | Interceptors, retry, caching |
| **Local DB** | Drift (SQLite) | Offline-first, type-safe |
| **Charts** | fl_chart | Finance-grade visualizations |
| **Forms** | flutter_form_builder | Complex form handling |

### 2.3 Infrastructure

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Hosting** | Render | Simple, Python-native |
| **Database** | Supabase | Postgres + Auth + Storage |
| **CDN** | Cloudflare | Performance, security |
| **Monitoring** | Sentry | Error tracking |
| **Analytics** | PostHog | Privacy-friendly analytics |

### 2.4 External Services

| Service | Purpose | Cost Estimate |
|---------|---------|---------------|
| **Plaid** | Financial data | $1-3/user/year |
| **Claude API** | AI features | $1-3/user/year |
| **Supabase** | Database + Auth | Free tier / $25/mo |
| **Render** | Backend hosting | Free tier / $7/mo |

---

## 3. Database Schema

### 3.1 Core Tables

```sql
-- User and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}'
);

-- Tax Profile
CREATE TABLE tax_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tax_year INTEGER NOT NULL,
    filing_status TEXT NOT NULL, -- single, married_jointly, etc.
    state TEXT NOT NULL,
    dependents INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, tax_year)
);

-- Plaid Connections
CREATE TABLE plaid_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    item_id TEXT NOT NULL,
    institution_id TEXT,
    institution_name TEXT,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accounts (from Plaid)
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plaid_item_id UUID REFERENCES plaid_items(id),
    account_id TEXT NOT NULL, -- Plaid account_id
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- depository, investment, loan
    subtype TEXT, -- checking, 401k, ira, etc.
    mask TEXT, -- last 4 digits
    current_balance DECIMAL(15,2),
    available_balance DECIMAL(15,2),
    currency TEXT DEFAULT 'USD',
    last_updated TIMESTAMP,
    UNIQUE(account_id)
);

-- Holdings (from Plaid)
CREATE TABLE holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    security_id TEXT,
    ticker TEXT,
    name TEXT,
    quantity DECIMAL(15,6),
    cost_basis DECIMAL(15,2),
    current_price DECIMAL(15,4),
    current_value DECIMAL(15,2),
    price_as_of DATE,
    holding_type TEXT, -- stock, etf, mutual_fund, etc.
    last_updated TIMESTAMP
);

-- Investment Transactions (from Plaid)
CREATE TABLE investment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_id TEXT UNIQUE NOT NULL,
    date DATE NOT NULL,
    type TEXT NOT NULL, -- buy, sell, dividend, etc.
    ticker TEXT,
    name TEXT,
    quantity DECIMAL(15,6),
    price DECIMAL(15,4),
    amount DECIMAL(15,2),
    fees DECIMAL(15,2) DEFAULT 0
);
```

### 3.2 Equity Compensation Tables

```sql
-- RSU Grants
CREATE TABLE rsu_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employer TEXT NOT NULL,
    ticker TEXT NOT NULL,
    grant_date DATE NOT NULL,
    total_shares INTEGER NOT NULL,
    vesting_schedule JSONB NOT NULL, -- [{date, shares}, ...]
    created_at TIMESTAMP DEFAULT NOW()
);

-- RSU Vest Events
CREATE TABLE rsu_vests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_id UUID REFERENCES rsu_grants(id) ON DELETE CASCADE,
    vest_date DATE NOT NULL,
    shares_vested INTEGER NOT NULL,
    fmv_at_vest DECIMAL(15,4),
    withheld_shares INTEGER,
    withheld_cash DECIMAL(15,2),
    net_shares INTEGER,
    state_worked TEXT, -- for multi-state sourcing
    UNIQUE(grant_id, vest_date)
);

-- ISO Grants
CREATE TABLE iso_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employer TEXT NOT NULL,
    ticker TEXT NOT NULL,
    grant_date DATE NOT NULL,
    expiration_date DATE NOT NULL,
    total_shares INTEGER NOT NULL,
    strike_price DECIMAL(15,4) NOT NULL,
    vesting_schedule JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ISO Exercises
CREATE TABLE iso_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_id UUID REFERENCES iso_grants(id) ON DELETE CASCADE,
    exercise_date DATE NOT NULL,
    shares_exercised INTEGER NOT NULL,
    fmv_at_exercise DECIMAL(15,4) NOT NULL,
    bargain_element DECIMAL(15,2) NOT NULL,
    shares_sold INTEGER DEFAULT 0,
    UNIQUE(grant_id, exercise_date)
);

-- ESPP Purchases
CREATE TABLE espp_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employer TEXT NOT NULL,
    ticker TEXT NOT NULL,
    offering_date DATE NOT NULL,
    purchase_date DATE NOT NULL,
    shares INTEGER NOT NULL,
    offering_price DECIMAL(15,4) NOT NULL,
    purchase_price DECIMAL(15,4) NOT NULL,
    fmv_at_purchase DECIMAL(15,4) NOT NULL,
    discount_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.3 Document and Tax Tables

```sql
-- Uploaded Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL, -- w2, 1099b, 1099div, etc.
    tax_year INTEGER NOT NULL,
    file_path TEXT,
    file_name TEXT,
    extracted_data JSONB,
    extraction_confidence DECIMAL(5,2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- W-2 Data (normalized from documents)
CREATE TABLE w2_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    tax_year INTEGER NOT NULL,
    employer_name TEXT,
    employer_ein TEXT,
    wages DECIMAL(15,2),
    federal_withheld DECIMAL(15,2),
    social_security_wages DECIMAL(15,2),
    social_security_withheld DECIMAL(15,2),
    medicare_wages DECIMAL(15,2),
    medicare_withheld DECIMAL(15,2),
    state TEXT,
    state_wages DECIMAL(15,2),
    state_withheld DECIMAL(15,2),
    box_12_codes JSONB, -- [{code, amount}, ...]
    box_14_other JSONB
);

-- 1099-B Data
CREATE TABLE form_1099b (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    tax_year INTEGER NOT NULL,
    broker TEXT,
    transactions JSONB -- [{description, date_sold, proceeds, cost_basis, ...}, ...]
);

-- Tax Estimates (calculated)
CREATE TABLE tax_estimates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tax_year INTEGER NOT NULL,
    estimated_income DECIMAL(15,2),
    estimated_federal_tax DECIMAL(15,2),
    estimated_state_tax DECIMAL(15,2),
    estimated_fica DECIMAL(15,2),
    estimated_niit DECIMAL(15,2),
    estimated_amt DECIMAL(15,2),
    total_estimated_tax DECIMAL(15,2),
    total_withheld DECIMAL(15,2),
    tax_gap DECIMAL(15,2),
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, tax_year)
);
```

### 3.4 Alert and Cache Tables

```sql
-- Active Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    alert_id TEXT NOT NULL, -- e.g., UW-001
    priority TEXT NOT NULL, -- CRITICAL, WARNING, INFO
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB, -- Alert-specific data
    dismissed BOOLEAN DEFAULT FALSE,
    dismissed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- AI Recommendation Cache
CREATE TABLE ai_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    cache_type TEXT NOT NULL, -- tax, investment, housing
    context_hash TEXT NOT NULL,
    recommendations JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    UNIQUE(user_id, cache_type, context_hash)
);

-- Financial Context Snapshot
CREATE TABLE financial_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tax_year INTEGER NOT NULL,
    context_data JSONB NOT NULL, -- Compact financial snapshot for AI
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, tax_year)
);
```

---

## 4. API Design

### 4.1 API Structure

```
/api/v1/
├── /auth
│   ├── POST   /login
│   ├── POST   /logout
│   └── GET    /me
├── /accounts
│   ├── GET    /              # List all accounts
│   ├── GET    /{id}          # Get account details
│   ├── GET    /net-worth     # Calculate net worth
│   └── POST   /sync          # Trigger Plaid sync
├── /tax
│   ├── GET    /estimate      # Current year estimate
│   ├── GET    /thermometer   # Tax gap visualization
│   ├── GET    /breakdown     # Detailed breakdown
│   └── GET    /history       # Prior year summaries
├── /portfolio
│   ├── GET    /holdings      # Current holdings
│   ├── GET    /allocation    # Asset allocation
│   ├── GET    /performance   # Returns/performance
│   └── GET    /transactions  # Investment transactions
├── /equity
│   ├── GET    /grants        # All equity grants
│   ├── POST   /grants/rsu    # Add RSU grant
│   ├── POST   /grants/iso    # Add ISO grant
│   ├── POST   /grants/espp   # Add ESPP purchase
│   ├── PUT    /grants/{id}   # Update grant
│   └── DELETE /grants/{id}   # Delete grant
├── /documents
│   ├── GET    /              # List documents
│   ├── POST   /upload        # Upload document
│   ├── GET    /{id}          # Get extracted data
│   ├── PUT    /{id}/verify   # Verify extraction
│   └── DELETE /{id}          # Delete document
├── /alerts
│   ├── GET    /              # Get active alerts
│   ├── POST   /{id}/dismiss  # Dismiss alert
│   └── POST   /refresh       # Refresh all alerts
├── /what-if
│   ├── POST   /rsu-sale      # RSU sale timing
│   ├── POST   /iso-exercise  # ISO exercise planning
│   ├── POST   /tax-loss      # Tax-loss harvesting
│   ├── POST   /roth-convert  # Roth conversion
│   └── POST   /relocate      # State relocation
├── /advisor
│   ├── GET    /tax           # AI tax recommendations
│   ├── GET    /investment    # AI investment advice
│   ├── POST   /housing       # AI housing analysis
│   └── POST   /refresh       # Force refresh cache
└── /sync
    ├── POST   /plaid/link    # Create Plaid link token
    ├── POST   /plaid/exchange # Exchange public token
    └── POST   /plaid/webhook # Plaid webhook handler
```

### 4.2 Request/Response Schemas

```python
# Tax Estimate Response
class TaxEstimateResponse(BaseModel):
    tax_year: int
    filing_status: str
    state: str

    # Income breakdown
    w2_income: Decimal
    rsu_income: Decimal
    iso_income: Decimal
    capital_gains: Decimal
    dividend_income: Decimal
    interest_income: Decimal
    other_income: Decimal
    total_income: Decimal

    # Tax breakdown
    federal_tax: Decimal
    state_tax: Decimal
    fica_tax: Decimal
    niit: Decimal
    amt: Decimal
    total_tax: Decimal

    # Withholding
    federal_withheld: Decimal
    state_withheld: Decimal
    fica_withheld: Decimal
    total_withheld: Decimal

    # Gap
    tax_gap: Decimal  # Positive = owe, Negative = refund
    gap_percentage: Decimal

    # Marginal rates
    federal_marginal_rate: Decimal
    state_marginal_rate: Decimal
    effective_rate: Decimal

    calculated_at: datetime


# What-If Request/Response
class WhatIfRSUSaleRequest(BaseModel):
    shares: int
    sell_year: int  # Current or next
    holding_period_months: int = 0


class WhatIfResponse(BaseModel):
    scenarios: List[ScenarioOutcome]
    optimal: str
    savings: Decimal
    recommendation: str
    warnings: List[str]


class ScenarioOutcome(BaseModel):
    name: str
    federal_tax: Decimal
    state_tax: Decimal
    niit: Decimal
    total_tax: Decimal
    effective_rate: Decimal
    notes: List[str]


# Alert Response
class AlertResponse(BaseModel):
    id: str
    alert_id: str
    priority: str
    category: str
    title: str
    message: str
    deadline: Optional[date]
    dismissed: bool
    created_at: datetime
```

### 4.3 Error Handling

```python
class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]]


# Standard error codes
ERRORS = {
    "AUTH_REQUIRED": (401, "Authentication required"),
    "FORBIDDEN": (403, "Access forbidden"),
    "NOT_FOUND": (404, "Resource not found"),
    "VALIDATION_ERROR": (422, "Validation error"),
    "PLAID_ERROR": (502, "Financial data service error"),
    "CALCULATION_ERROR": (500, "Tax calculation error"),
    "RATE_LIMIT": (429, "Rate limit exceeded"),
}
```

---

## 5. Tax Calculation Engine

### 5.1 Engine Architecture

```python
class TaxEngine:
    """Core tax calculation engine."""

    def __init__(self):
        self.federal = FederalTaxCalculator()
        self.state = StateTaxCalculatorFactory()
        self.fica = FICATaxCalculator()
        self.niit = NIITCalculator()
        self.amt = AMTCalculator()

    def calculate(
        self,
        income: IncomeData,
        deductions: DeductionData,
        credits: CreditData,
        filing_status: FilingStatus,
        state: str,
        tax_year: int,
    ) -> TaxResult:
        """Calculate complete tax liability."""

        # Federal income tax
        federal = self.federal.calculate(
            income=income.total_ordinary,
            deductions=deductions.total,
            credits=credits.total,
            filing_status=filing_status,
            tax_year=tax_year,
        )

        # Capital gains
        capital_gains = self.federal.calculate_capital_gains(
            short_term=income.short_term_gains,
            long_term=income.long_term_gains,
            ordinary_income=income.total_ordinary - income.capital_gains,
            filing_status=filing_status,
            tax_year=tax_year,
        )

        # FICA
        fica = self.fica.calculate(
            wages=income.wages,
            self_employment=income.self_employment,
            tax_year=tax_year,
        )

        # NIIT
        niit = self.niit.calculate(
            investment_income=income.investment_income,
            agi=income.agi,
            filing_status=filing_status,
        )

        # AMT
        amt = self.amt.calculate(
            regular_tax=federal.tax,
            amti=self._calculate_amti(income, deductions),
            iso_adjustment=income.iso_bargain_element,
            filing_status=filing_status,
            tax_year=tax_year,
        )

        # State tax
        state_calc = self.state.get_calculator(state)
        state_tax = state_calc.calculate(
            income=income,
            filing_status=filing_status,
            tax_year=tax_year,
        )

        return TaxResult(
            federal_tax=federal.tax + capital_gains.tax,
            state_tax=state_tax.tax,
            fica_tax=fica.tax,
            niit=niit.tax,
            amt=max(Decimal('0'), amt.tax - federal.tax),
            total_tax=self._sum_taxes(federal, capital_gains, fica, niit, amt, state_tax),
            marginal_rates=self._calculate_marginal_rates(...),
            effective_rate=self._calculate_effective_rate(...),
        )
```

### 5.2 Calculation Performance

| Calculation | Target Time | Strategy |
|-------------|-------------|----------|
| Single tax estimate | < 50ms | In-memory, no I/O |
| What-if scenario | < 100ms | Cached base data |
| Full year projection | < 200ms | Parallel calculations |
| Multi-year analysis | < 500ms | Incremental caching |

### 5.3 Accuracy Testing

```python
class TaxEngineTests:
    """Test cases for tax calculation accuracy."""

    def test_federal_brackets_single(self):
        """Test federal tax brackets for single filer."""
        test_cases = [
            (50_000, 5_544),     # 12% bracket
            (100_000, 14_768),   # 22% bracket
            (200_000, 38_836),   # 32% bracket
            (500_000, 136_836),  # 35% bracket
            (1_000_000, 321_836), # 37% bracket
        ]
        for income, expected_tax in test_cases:
            result = self.engine.calculate_federal(income, "single", 2025)
            assert abs(result - expected_tax) < 1, f"Failed for {income}"

    def test_amt_on_iso(self):
        """Test AMT calculation on ISO exercise."""
        # $500K income + $200K ISO bargain element
        result = self.engine.calculate(
            income=IncomeData(wages=500_000, iso_bargain_element=200_000),
            filing_status="single",
            tax_year=2025,
        )
        assert result.amt > 0, "AMT should be triggered"
```

---

## 6. Performance Requirements

### 6.1 API Performance

| Endpoint Type | P50 Latency | P99 Latency | Throughput |
|---------------|-------------|-------------|------------|
| Read (simple) | < 50ms | < 200ms | 1000 req/s |
| Read (complex) | < 100ms | < 500ms | 500 req/s |
| Write | < 100ms | < 500ms | 200 req/s |
| Calculation | < 200ms | < 1s | 100 req/s |
| AI (Claude) | < 2s | < 5s | 10 req/s |

### 6.2 Mobile Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cold start | < 2s | First paint |
| Screen transition | < 100ms | Navigation |
| List scroll | 60fps | Frame rate |
| Search | < 200ms | Results appear |
| Offline support | Full read | Cached data |

### 6.3 Data Sync

| Operation | Frequency | Duration |
|-----------|-----------|----------|
| Plaid refresh | Daily | < 30s |
| Holdings update | Real-time | < 5s |
| Tax recalculation | On change | < 500ms |
| Alert evaluation | Hourly | < 10s |

---

## 7. Security

### 7.1 Authentication

```python
# JWT-based authentication
class AuthConfig:
    algorithm = "HS256"
    access_token_expire = timedelta(hours=24)
    refresh_token_expire = timedelta(days=30)

# API key for server-to-server
class APIKeyAuth:
    header = "X-API-Key"
    hash_algorithm = "sha256"
```

### 7.2 Data Encryption

| Data Type | At Rest | In Transit |
|-----------|---------|------------|
| Credentials | AES-256 | TLS 1.3 |
| Financial data | AES-256 | TLS 1.3 |
| Documents | AES-256 | TLS 1.3 |
| Cache | Encrypted | TLS 1.3 |

### 7.3 Plaid Token Security

```python
# Plaid access tokens are encrypted before storage
def encrypt_plaid_token(access_token: str) -> str:
    key = get_encryption_key()
    fernet = Fernet(key)
    return fernet.encrypt(access_token.encode()).decode()

def decrypt_plaid_token(encrypted_token: str) -> str:
    key = get_encryption_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_token.encode()).decode()
```

---

## 8. Deployment

### 8.1 Development Environment

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./taxlens.db
      - PLAID_CLIENT_ID=${PLAID_CLIENT_ID}
      - PLAID_SECRET=${PLAID_SECRET}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
```

### 8.2 Production (Render)

```yaml
# render.yaml
services:
  - type: web
    name: taxlens-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: taxlens-db
          property: connectionString
      - key: PLAID_CLIENT_ID
        sync: false
      - key: PLAID_SECRET
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false

databases:
  - name: taxlens-db
    databaseName: taxlens
    plan: starter
```

### 8.3 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
```

---

## 9. Monitoring

### 9.1 Logging

```python
# Structured logging
import structlog

logger = structlog.get_logger()

logger.info(
    "tax_calculation_completed",
    user_id=user.id,
    tax_year=2025,
    duration_ms=elapsed,
    result_total=result.total_tax,
)
```

### 9.2 Metrics

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| API latency | Histogram | P99 > 1s |
| Error rate | Counter | > 1% |
| Calculation accuracy | Gauge | Deviation > $100 |
| Plaid sync failures | Counter | > 5/hour |
| Claude API errors | Counter | > 10/hour |

### 9.3 Health Checks

```python
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "plaid": await check_plaid(),
        "claude": await check_claude(),
    }
    all_healthy = all(checks.values())
    return {"status": "healthy" if all_healthy else "degraded", "checks": checks}
```

---

## 10. Implementation Phases

### Phase 1: Core Backend (Weeks 1-3)

| Task | Effort | Priority |
|------|--------|----------|
| FastAPI project setup | 4 hrs | P0 |
| Database schema + migrations | 8 hrs | P0 |
| Federal tax calculator | 16 hrs | P0 |
| Plaid integration | 12 hrs | P0 |
| Basic API endpoints | 12 hrs | P0 |

### Phase 2: Flutter MVP (Weeks 4-7)

| Task | Effort | Priority |
|------|--------|----------|
| Flutter project setup | 4 hrs | P0 |
| Dashboard screen | 12 hrs | P0 |
| Tax thermometer | 8 hrs | P0 |
| Holdings view | 8 hrs | P1 |
| Document upload | 12 hrs | P1 |

### Phase 3: Advanced Features (Weeks 8-10)

| Task | Effort | Priority |
|------|--------|----------|
| State tax calculators | 16 hrs | P0 |
| Alert engine | 12 hrs | P0 |
| What-if scenarios | 16 hrs | P1 |
| AI advisor integration | 12 hrs | P1 |

---

## 11. Sources

### Frameworks
- FastAPI: https://fastapi.tiangolo.com/
- Flutter: https://flutter.dev/docs
- SQLAlchemy: https://docs.sqlalchemy.org/

### Services
- Plaid: https://plaid.com/docs/
- Claude API: https://docs.anthropic.com/
- Supabase: https://supabase.com/docs

### Security
- OWASP API Security: https://owasp.org/www-project-api-security/
- Plaid Security: https://plaid.com/security/

---

*Document generated as part of TaxLens Phase 1 Research*
