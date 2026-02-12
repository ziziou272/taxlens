# TaxLens Tools & Skills Reference Guide

> **Last updated:** 2026-02-12  
> **Project:** TaxLens — AI-powered personal tax optimization app (Flutter + FastAPI + Supabase)

---

## Table of Contents

1. [Installed Skills Reference](#1-installed-skills-reference)
2. [Tax Engine Validation & Enhancement Plan](#2-tax-engine-validation--enhancement-plan)
3. [Flutter Package Recommendations](#3-flutter-package-recommendations)
4. [Reference Flutter Finance Apps](#4-reference-flutter-finance-apps-open-source)

---

## 1. Installed Skills Reference

All skills installed in `/root/.openclaw/workspace/skills/`.

### 🦋 Frontend — Flutter

| Skill | What It Is | TaxLens Use Cases | Key Patterns |
|-------|-----------|-------------------|--------------|
| **flutter** | Flutter development best practices — widgets, state management, performance, navigation, testing | Every screen in TaxLens. Widget composition for tax forms, `ListView.builder` for transaction lists, `go_router` for deep linking, `const` constructors for static tax category cards | `const` constructors everywhere; `FutureBuilder` futures cached in `initState`; `RepaintBoundary` around chart widgets; `MediaQuery.sizeOf(context)` not `.of(context)` |

**Key rules from the skill:**
- Split large `build()` into smaller widgets (not helper methods)
- `ValueNotifier` + `ValueListenableBuilder` for simple local state (e.g., toggle between tax years)
- Cache `Future` in `initState` — never create inline in `FutureBuilder`
- Always check `mounted` after `await` before calling `setState`
- Use `flutter run --profile` for real perf testing

### ⚡ Backend — FastAPI / Python

| Skill | What It Is | TaxLens Use Cases | Key Patterns |
|-------|-----------|-------------------|--------------|
| **fastapi** | FastAPI patterns — async, Pydantic v2, dependency injection, lifespan, testing | Tax calculation API, Plaid webhook receiver, PDF report generation endpoints, user auth | `lifespan` context manager (not deprecated `on_event`); `Depends()` for DB sessions with `yield`; `Annotated` types for reusable validation; `httpx.AsyncClient` for async tests |
| **sw-python-backend** | Full Python backend expertise — SQLAlchemy 2.0, Celery, pandas, ML integration | Database models for tax records, Alembic migrations, background tax computation jobs, CSV import processing | SQLAlchemy async sessions; Pydantic v2 `model_validate()`/`model_dump()`; Celery for long-running tax optimization calculations |

**Key rules:**
- Use async DB drivers (`asyncpg`) — sync drivers block the event loop
- `BackgroundTasks` for quick post-response work; Celery for heavy tax computations
- Override dependencies in tests: `app.dependency_overrides[get_db] = mock_db`
- Return `dict` from endpoints (not Pydantic models) for speed
- `status_code=201` on POST endpoints

### 🗄️ Data — Supabase / Plaid

| Skill | What It Is | TaxLens Use Cases | Key Patterns |
|-------|-----------|-------------------|--------------|
| **supabase** | Supabase CLI for queries, CRUD, vector search, table management | User profiles, tax document storage, transaction categorization DB, vector search for tax deduction matching | `scripts/supabase.sh query "SQL"` for raw queries; `select` with `--eq` filters; `vector-search` for semantic deduction lookup |
| **plaid** | Plaid CLI for linking bank accounts, fetching balances/transactions | Auto-import user financial transactions, categorize income/expenses for Schedule C, detect W-2 vs 1099 income patterns | `plaid-cli transactions <alias> --from YYYY-MM-DD --to YYYY-MM-DD --output-format json`; pipe through `jq` for category filtering |

**Key rules:**
- Never print/log Plaid secrets or access tokens
- Supabase requires `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` env vars
- Use Plaid aliases for cleaner scripts
- Monitor transactions by comparing transaction IDs across polling windows

### 💰 Finance Domain

| Skill | What It Is | TaxLens Use Cases | Key Patterns |
|-------|-----------|-------------------|--------------|
| **personal-finance** | Expense tracking, budgets, EMI reminders with SQLite backend | Track user spending categories, budget vs actual for tax planning, estimated tax payment reminders (quarterly 1040-ES) | `scripts/init_db.py` for DB setup; preset categories (Food, Rent, etc.); scheduled reminders for recurring payments |
| **cfo** | Strategic financial leadership — forecasting, cash management, reporting | Tax liability forecasting across scenarios (best/base/worst), cash flow projections for estimated payments, variance analysis between projected and actual tax burden | Rolling forecasts; scenario planning; 13-week cash flow; driver-based models |
| **financial-design-systems** | Dark-themed financial chart patterns, color palettes for gains/losses | Tax dashboard UI theming — green for refunds, red for amounts owed; consistent chart styling across all visualizations | `chartColors.positive` (green) / `chartColors.negative` (red); dark surface backgrounds; monospace fonts for financial figures |

### 📊 Visualization

| Skill | What It Is | TaxLens Use Cases | Key Patterns |
|-------|-----------|-------------------|--------------|
| **data-visualization** | Matplotlib/Seaborn/Plotly charts for data analysis | Server-side chart generation for tax reports — cost breakdowns, income distribution, year-over-year comparison | `create_cost_breakdown_pie()` for tax category splits; horizontal bar charts for deduction comparisons |
| **chart-image** | Headless PNG chart generation via Vega-Lite (no browser needed) | Generate chart images for push notifications, email reports, PDF tax summaries | `node chart.mjs --type pie --data '[...]' --output chart.png`; supports line, bar, area, pie, donut, candlestick, heatmap |

**Chart-image setup:** `cd skills/chart-image/scripts && npm install`

### 🧪 Testing

| Skill | What It Is | TaxLens Use Cases | Key Patterns |
|-------|-----------|-------------------|--------------|
| **test-master** | Comprehensive testing strategy — unit, integration, E2E, performance, security | Tax calculation accuracy tests, API endpoint testing, load testing during tax season, security testing for PII (SSN, financial data) | Three modes: `[Test]` functional, `[Perf]` performance, `[Security]` vulnerability; reference docs in `references/` subdirectory |
| **sw-ui-testing** | Cypress + Testing Library for UI tests | Widget/component testing for tax forms, E2E flows for filing wizard, API mocking for Plaid integration tests | Cypress `cy.intercept()` for API mocking; Testing Library user-centric queries; custom commands for reusable login flows |

---

## 2. Tax Engine Validation & Enhancement Plan

**Goal:** Validate the TaxLens Python tax engine (`/tmp/taxlens`, repo: `ziziou272/taxlens`) against established open-source tax calculators, and borrow logic for missing features.

### 2.1 PSLmodels/Tax-Calculator

| | Details |
|---|---|
| **Repository** | [github.com/PSLmodels/Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator) |
| **What it provides** | US federal individual income tax + payroll tax microsimulation. Models tax brackets, deductions, credits, AMT, FICA, NIIT. Policy parameter database with historical values. |
| **License** | MIT ✅ (compatible with TaxLens MIT) |
| **Install** | `pip install taxcalc` (or `conda install -c conda-forge taxcalc`) |

**Validation tests to run:**

```python
# 1. Federal bracket validation
# Create identical taxpayer profiles in both engines, compare:
# - Single filer, $75K wages → federal tax
# - MFJ, $150K wages + $20K capital gains → federal tax
# - HoH, $50K wages, 2 dependents → federal tax + child credit

# 2. AMT validation
# High-income scenarios with ISO stock options, large SALT

# 3. Payroll tax (FICA + NIIT)
# W-2 wages at various levels (below/above SS cap)
# Self-employment income for SE tax
# High earner with $250K+ for NIIT (3.8%)

# 4. Standard vs itemized deduction crossover
```

**What to borrow/reference:**
- Tax parameter files (JSON) with bracket thresholds, phase-outs, credit amounts by year
- AMT calculation logic (complex, easy to get wrong)
- EITC phase-in/phase-out curves
- Policy reform simulation architecture (useful for "what-if" scenarios in TaxLens)

### 2.2 PolicyEngine/policyengine-us

| | Details |
|---|---|
| **Repository** | [github.com/PolicyEngine/policyengine-us](https://github.com/PolicyEngine/policyengine-us) |
| **What it provides** | Complete US tax-benefit rules engine covering federal + ALL 50 states. Income tax, payroll tax, benefits (SNAP, Medicaid, etc.). Most comprehensive state tax coverage available. |
| **License** | AGPL-3.0 ⚠️ (cannot copy code directly into MIT TaxLens — use as **reference only** for validation and algorithm design) |
| **Install** | `pip install policyengine-us` |

**Validation tests to run:**

```python
from policyengine_us import Simulation

# 1. California state tax validation
# Compare CA income tax for various AGI levels against TaxLens CA module

# 2. Federal + state combined scenarios
# Verify total tax liability matches across engines

# 3. State-specific deductions and credits
# CA renter's credit, CA EITC, etc.

# 4. Use as reference to ADD new state modules:
#    - New York (complex: city tax, MCTMT, Yonkers surcharge)
#    - Washington (no income tax, but capital gains tax since 2022)
#    - Texas, Florida (no income tax — verify $0 state liability)
```

**What to reference (not copy — AGPL):**
- State tax calculation logic structure (how they organize 50 states)
- Variable dependency graphs for tax calculations
- Benefit phase-out interactions with income
- Their test cases as validation data points

### 2.3 PolicyEngine/policyengine-taxsim

| | Details |
|---|---|
| **Repository** | [github.com/PolicyEngine/policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim) |
| **What it provides** | TAXSIM-compatible API emulator. Takes TAXSIM-format input, returns tax calculations. Good for automated batch cross-validation. |
| **License** | AGPL-3.0 ⚠️ (reference only) |
| **Install** | `pip install policyengine-taxsim` |

**Validation approach:**

```bash
# Create TAXSIM-format CSV with test scenarios
# Run through policyengine-taxsim
# Run same scenarios through TaxLens engine
# Diff outputs automatically

# TAXSIM input format (CSV):
# taxsimid, year, state, mstat, page, sage, depx, pwages, swages, ...
```

**What to reference:**
- TAXSIM input/output format as a standardized test interface
- Build a TAXSIM-compatible input adapter for TaxLens → enables automated regression testing against any TAXSIM-compatible engine
- Their test fixture files as ready-made validation datasets

### 2.4 mmacpherson/tenforty

| | Details |
|---|---|
| **Repository** | [github.com/mmacpherson/tenforty](https://github.com/mmacpherson/tenforty) |
| **What it provides** | Lightweight Python library for US federal tax + some states. Simpler than Tax-Calculator, closer to form-level calculations (1040, Schedule A/B/C/D). |
| **License** | MIT ✅ (compatible — can borrow code directly) |
| **Install** | `pip install tenforty` (or clone and install) |

**Validation tests to run:**

```python
# 1. Form-level validation
# Compare line-by-line on Form 1040
# Schedule C (self-employment) calculations
# Schedule D (capital gains) with various holding periods

# 2. Simple scenarios first
# W-2 only, standard deduction
# W-2 + 1099-INT + 1099-DIV
# Self-employed with business expenses
```

**What to borrow (MIT — can copy):**
- Form-based calculation structure (maps cleanly to IRS forms)
- Tax table lookup logic
- Filing status determination helpers
- Line-by-line calculation chains

### Validation Execution Plan

```
Phase 1: Setup (Day 1)
├── Clone TaxLens engine to /tmp/taxlens
├── pip install taxcalc policyengine-us policyengine-taxsim
├── Clone tenforty
└── Create shared test fixture JSON with 20 taxpayer scenarios

Phase 2: Federal Validation (Days 2-3)
├── Run all 20 scenarios through Tax-Calculator → baseline
├── Run same through TaxLens → compare
├── Run through tenforty → triple-check
├── Document discrepancies with line-by-line analysis
└── Fix TaxLens engine where it diverges

Phase 3: State Validation (Days 4-5)
├── Run CA scenarios through policyengine-us → baseline
├── Compare with TaxLens CA module
├── Generate reference data for NY, WA modules
└── Build state module templates from policyengine-us patterns

Phase 4: Regression Suite (Day 6)
├── Build TAXSIM-format adapter for TaxLens
├── Create automated comparison pipeline
└── Add to CI: every PR runs validation against all 3 engines
```

---

## 3. Flutter Package Recommendations

| Package | Version | Purpose | TaxLens Context |
|---------|---------|---------|-----------------|
| `fl_chart` | ^0.69.0 | Charts (line, bar, pie, radar) | Tax breakdown pie charts, income vs deductions bar charts, monthly withholding trends |
| `flutter_riverpod` | ^2.6.0 | State management | App-wide state: user profile, tax data, calculation results. Selective rebuilds for perf |
| `drift` | ^2.22.0 | Type-safe SQLite ORM | Local cache of tax records, offline-first transactions, migration support |
| `drift_flutter` | ^0.2.0 | Flutter bindings for drift | Platform-specific SQLite initialization |
| `dio` | ^5.7.0 | HTTP client | FastAPI communication, interceptors for auth tokens, retry logic |
| `flutter_secure_storage` | ^9.2.0 | Encrypted key-value storage | Store SSN, bank account numbers, API tokens. Uses Keychain (iOS) / Keystore (Android) |
| `local_auth` | ^2.3.0 | Biometric authentication | Require Face ID / fingerprint before showing sensitive tax data |
| `file_picker` | ^8.1.0 | File selection | Upload W-2 PDFs, 1099 CSVs, receipt images for deduction documentation |
| `syncfusion_flutter_charts` | ^27.1.0 | Premium financial charts | Waterfall charts for tax flow, stacked bars for income sources, sparklines in summaries |
| `freezed` | ^2.5.0 | Immutable data classes + unions | Tax form models, calculation state (loading/success/error), API response types |
| `json_serializable` | ^6.8.0 | JSON serialization codegen | API request/response models, local storage serialization |
| `intl` | ^0.19.0 | i18n, number/date formatting | Currency formatting (`$12,345.67`), date formatting for tax deadlines |
| `go_router` | ^14.6.0 | Declarative routing | Deep links to specific tax forms, URL-based navigation for web, auth guards |
| `pdf` | ^3.11.0 | PDF generation | Generate tax summary reports, estimated payment vouchers |
| `printing` | ^5.13.0 | Print/share PDFs | Print or share generated tax reports |

### `pubspec.yaml` snippet

```yaml
dependencies:
  flutter_riverpod: ^2.6.0
  dio: ^5.7.0
  go_router: ^14.6.0
  fl_chart: ^0.69.0
  drift: ^2.22.0
  drift_flutter: ^0.2.0
  flutter_secure_storage: ^9.2.0
  local_auth: ^2.3.0
  file_picker: ^8.1.0
  intl: ^0.19.0
  pdf: ^3.11.0
  printing: ^5.13.0
  freezed_annotation: ^2.4.0
  json_annotation: ^4.9.0

dev_dependencies:
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  build_runner: ^2.4.0
  drift_dev: ^2.22.0

# Syncfusion (requires free community license for <$1M revenue)
  syncfusion_flutter_charts: ^27.1.0
```

---

## 4. Reference Flutter Finance Apps (Open Source)

### innthomas/tax_app
- **Repo:** [github.com/innthomas/tax_app](https://github.com/innthomas/tax_app)
- **What:** Flutter personal income tax calculator
- **Learn from:** Tax form input UI patterns, how they structure tax bracket logic in Dart, filing status selection flow
- **Borrow:** Form layout patterns for W-2 input, tax summary result screens

### Finance-App-Open-Source/finance-app-flutter
- **Repo:** [github.com/nicloay/finance-app-flutter](https://github.com/nicloay/finance-app-flutter) (or search "finance app flutter open source")
- **What:** Finance dashboard template with charts and transaction lists
- **Learn from:** Dashboard layout with summary cards + chart + recent transactions, category-based spending breakdowns
- **Borrow:** Card-based summary widgets, bottom navigation patterns, transaction list tile design

### floranguyen0/mmas-money-tracker
- **Repo:** [github.com/floranguyen0/mmas-money-tracker](https://github.com/floranguyen0/mmas-money-tracker)
- **What:** Full expense tracker with categories, budgets, reports
- **Learn from:** Category management UI, date range pickers for filtering, spending report visualizations
- **Borrow:** Category icon/color picker, monthly calendar view with spending indicators, export functionality

### deriv-com/flutter-chart
- **Repo:** [github.com/deriv-com/flutter-chart](https://github.com/deriv-com/flutter-chart)
- **What:** Professional financial charting library (candlestick, OHLC, technical indicators)
- **Learn from:** High-performance canvas rendering for large datasets, gesture handling (pinch-zoom, pan), real-time data streaming
- **Borrow:** Chart gesture interaction patterns, crosshair/tooltip implementation, time-axis scaling logic

---

## Quick Reference: Skill Invocation

| Need | Skill to Load | Key Command/Pattern |
|------|--------------|---------------------|
| Build a Flutter screen | `flutter` | Follow widget splitting rules, `const` constructors |
| Create API endpoint | `fastapi` | `lifespan` setup, `Depends()` injection, Pydantic v2 |
| Query Supabase | `supabase` | `scripts/supabase.sh query "SQL"` |
| Fetch transactions | `plaid` | `plaid-cli transactions <alias> --from --to --output-format json` |
| Design chart UI | `financial-design-systems` | Use `chartColors` palette, dark theme patterns |
| Generate chart image | `chart-image` | `node chart.mjs --type <type> --data '<json>' --output file.png` |
| Server-side plots | `data-visualization` | Matplotlib/Seaborn/Plotly patterns |
| Budget tracking logic | `personal-finance` | SQLite categories, scheduled reminders |
| Financial strategy | `cfo` | Scenario planning, cash flow forecasting |
| Write tests | `test-master` | Load `references/` subdocs per test type |
| UI component tests | `sw-ui-testing` | Cypress commands, Testing Library queries |
| Backend architecture | `sw-python-backend` | SQLAlchemy async, Celery workers, pandas ETL |
