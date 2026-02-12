# Changelog

All notable changes to TaxLens will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-02-12

### Added

#### FastAPI Backend (PR #17)
- Full FastAPI backend with 11+ REST endpoints
- Tax calculation, alerts, and what-if scenario APIs
- SQLAlchemy 2.0 async with SQLite persistence
- Pydantic v2 request/response schemas
- API docs served at `/docs` (Swagger UI)

#### Multi-State Income Sourcing (PR #16)
- 183-day residency threshold rule
- RSU income allocation across states
- Part-year move support with date-based sourcing
- Day-count tracking for remote work across state lines

#### Engine Cross-Validation Suite (PR #15)
- 20 comprehensive tax scenarios validated against IRS reference values
- 0 discrepancies across all scenarios
- Covers single, married, HoH filing statuses
- AMT, NIIT, LTCG, and equity edge cases validated

#### New York State Tax Module (PR #14)
- New York state income tax (all brackets)
- NYC resident tax
- Yonkers resident/nonresident surcharge
- Integration with multi-state sourcing

#### Washington State Tax Module (PR #13)
- Washington capital gains tax (7% on gains > $270K)
- Long-term capital gains only
- Proper exemption threshold handling

### Improved
- Test count increased to 520+ with 82%+ coverage
- Red flag count now at 73+ automated alerts
- What-if engine expanded to 23 scenario types

---

## [0.2.0] - 2025-02-01

### Added

#### Phase 3: Data Integration
- **E*TRADE CSV Importer**: Full support for parsing E*TRADE transaction exports
  - RSU vesting detection
  - ISO/NSO exercise tracking
  - ESPP purchase identification
  - Sales with cost basis
- **Robinhood CSV Importer**: Support for retail trading data
  - Buy/sell transaction parsing
  - Dividend tracking
  - Cost basis calculation (FIFO)
  - Gain/loss calculation
- **Manual Entry Data Models**: Comprehensive models for hand-entered data
  - `W2Entry`: Complete W-2 form data with Box 12 codes
  - `EquityGrantEntry`: Track grants with vesting schedules
  - `VestingEventEntry`: Record individual vesting events
  - `OptionExerciseEntry`: ISO/NSO exercise with AMT tracking
  - `StockSaleEntry`: Sales with automatic holding period calculation
  - `OtherIncomeEntry`: Dividends, interest, rental, etc.
  - `EstimatedPaymentEntry`: Quarterly estimated tax payments
  - `TaxProfile`: Combine all entries for complete tax picture

#### Phase 4: Enhanced Red Flag System
- **Estimated Payment Deadlines**: Track all quarterly deadlines (Apr 15, Jun 15, Sep 15, Jan 15)
  - Automatic deadline detection
  - Critical alerts for imminent deadlines (< 7 days)
  - Warnings for missed or underpaid quarters
  - Safe harbor calculation against prior year
- **Quarterly Underwithholding Check**: Year-to-date pace analysis
  - Compare YTD withholding vs projected tax
  - Alert when behind pace
  - Detect accelerating income (equity events)
- **State Nexus Warnings**: Multi-state tax complexity alerts
  - Residency threshold detection (183-day rule)
  - Work-day taxation for remote work in other states
  - Part-year move detection
  - Special handling for no-income-tax states (WA, TX, FL, etc.)
- **Wash Sale Detection**: 30-day window monitoring
  - Detect buy-after-sell violations
  - Detect buy-before-sell violations
  - Partial share matching
  - Planning mode: warns about active wash sale windows
- **Alert Priority System**: Intelligent alert sorting
  - `IMMEDIATE`: Critical issues, past deadlines
  - `THIS_WEEK`: Deadlines within 7 days, amounts > $5K
  - `THIS_MONTH`: Deadlines within 30 days, amounts > $1K
  - `PLANNING`: Future planning items

#### Phase 5: What-If Tax Scenario Engine
- **WhatIfEngine**: Core scenario comparison engine
  - Set baseline scenario
  - Add unlimited alternative scenarios
  - Compare scenarios with tax delta
  - Find best (lowest tax) scenario
  - Generate comprehensive summaries
- **Scenario Builders**: Pre-built scenario generators
  - `create_rsu_timing_scenarios`: Vest now vs defer to next year
  - `create_iso_exercise_scenarios`: Model different exercise amounts
  - `create_bonus_timing_scenarios`: Current year vs deferral
  - `create_state_move_scenarios`: Compare CA vs WA, etc.
  - `create_capital_gains_timing_scenarios`: Realize vs defer gains
- **Analysis Functions**:
  - `calculate_marginal_tax_impact`: Model additional income impact
  - `find_optimal_iso_exercise`: Binary search for AMT-optimal exercise
  - `generate_optimization_recommendations`: Auto-suggest tax strategies
- **Comprehensive Tax Calculations**:
  - Federal tax with all 7 brackets
  - LTCG/QDIV preferential rates (0%, 15%, 20%)
  - AMT calculation for ISO exercises
  - FICA (Social Security + Medicare + Additional Medicare)
  - NIIT (3.8% on investment income above threshold)
  - California state tax with mental health services tax
  - Estimates for 15+ other states
  - No-income-tax state handling

#### Phase 6: Polish & Tests
- **Integration Tests**: End-to-end workflow validation
  - Tech employee full year calculation
  - ISO exercise with AMT impact
  - RSU vesting to sale flow
  - Data import to calculation pipeline
  - Multi-state scenario handling
  - Wash sale detection flow
  - Complete what-if workflow
- **Documentation**: Comprehensive CHANGELOG

### Improved
- Test coverage increased from 73% to 85%+
- Federal tax calculations now include all filing statuses
- AMT calculation properly compares TMT vs regular tax
- LTCG tax properly "stacks" on ordinary income

### Fixed
- Corrected function signatures for `calculate_fica`, `calculate_ltcg_tax`, `calculate_niit`
- AMT calculation now returns actual AMT owed (TMT - regular tax)
- State tax calculation for California returns Decimal directly

## [0.1.0] - 2025-01-15

### Added

#### Phase 1: Core Engine
- **Federal Tax Calculator**: 2025 tax bracket calculations
  - All 7 brackets for Single, MFJ, MFS, HoH
  - Standard deduction handling
  - Marginal rate calculation
- **AMT Calculator**: Alternative Minimum Tax
  - AMT exemption and phaseout
  - 26%/28% AMT rates
  - ISO bargain element handling
- **FICA Calculator**: Employment taxes
  - Social Security (6.2% up to wage base)
  - Medicare (1.45%)
  - Additional Medicare (0.9% above threshold)
- **NIIT Calculator**: Net Investment Income Tax
  - 3.8% on investment income above threshold
  - Threshold varies by filing status
- **California Tax Calculator**: State income tax
  - 9 brackets up to 13.3%
  - Mental health services tax (1% above $1M)
  - SDI calculation

#### Phase 2: Equity Intelligence
- **RSU Calculator**: Restricted Stock Unit tracking
  - Vesting schedule handling
  - Ordinary income at vest
  - Cost basis for sales
- **ISO Calculator**: Incentive Stock Option support
  - Exercise tracking
  - Bargain element calculation
  - AMT preference items
  - Qualifying vs disqualifying dispositions
- **NSO Calculator**: Non-Qualified Stock Option support
  - Exercise income calculation
  - Withholding requirements
- **ESPP Calculator**: Employee Stock Purchase Plan
  - Lookback provision support
  - Qualifying vs disqualifying dispositions
  - Ordinary income vs capital gain splitting

### Data Models
- `FilingStatus`: Single, MFJ, MFS, HoH
- `TaxYear`: Configuration for tax year parameters
- `IncomeBreakdown`: Categorized income tracking
- `TaxSummary`: Complete calculation results
- `EquityGrant`: Equity compensation tracking

### Importers
- **Fidelity CSV Parser**: NetBenefits export support
- **Schwab CSV Parser**: Equity Award Center support

### Red Flags System
- Underwithholding detection
- RSU withholding gap analysis
- AMT trigger warnings
- Washington State capital gains tax
- NIIT threshold alerts
- Estimated payment requirements

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.3.0 | 2025-02-12 | NY/WA state tax, multi-state sourcing, cross-validation, FastAPI backend |
| 0.2.0 | 2025-02-01 | Data integration, enhanced red flags, what-if engine |
| 0.1.0 | 2025-01-15 | Core engine, equity calculations, basic red flags |

## Coming Soon

### v0.4.0 (Planned)
- Plaid integration for automatic data import
- Real-time stock price fetching
- Tax loss harvesting suggestions

### v1.0.0 (Future)
- Production-ready release
- Security audit complete
- Public beta launch
