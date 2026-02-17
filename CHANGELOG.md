# Changelog

All notable changes to TaxLens will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-02-17

### Added

#### Feature: Previous Year Tax Return Import (Phase B — PDF + AI Extraction)
- **Design doc**: `docs/design-review-previous-year.md` — full feature spec (import methods, data model, phases, API, UI)
- **New model**: `TaxReturn` SQLAlchemy model (`app/models/tax_return.py`) — stores all 1040 key fields
- **New service**: `tax_return_service.py` — PDF/image upload, Gemini Vision extraction, confidence scoring, Supabase upsert
- **New router**: `app/routers/tax_returns.py` — 5 endpoints under `/api/tax-returns`
- **New schemas**: `app/schemas/tax_return.py` — `TaxReturnExtractResponse`, `TaxReturnConfirmRequest`, `TaxReturnResponse`, `TaxReturnSummary`
- **Supabase migration**: `packages/api/migrations/001_tax_returns.sql` — `tax_returns` table with RLS, index, and trigger
- **New config key**: `TAXLENS_GEMINI_API_KEY` — Google Gemini API for Vision extraction
- **New dependencies**: `google-generativeai>=0.8.0`, `PyMuPDF>=1.24.0`, `httpx>=0.27.0`

#### API Endpoints — `/api/tax-returns`
- `POST /api/tax-returns/upload-pdf` — accepts 1040 PDF/image, extracts fields via Gemini Vision, returns with confidence scores
- `POST /api/tax-returns/confirm` — user confirms extracted data, saves to DB + Supabase
- `GET /api/tax-returns` — list all years (year switcher dropdown data)
- `GET /api/tax-returns/{tax_year}` — get full return for a year
- `DELETE /api/tax-returns/{tax_year}` — delete a year's data

#### Key 1040 Fields Extracted by AI
Filing status, AGI, total income, deduction type/amount, taxable income, total tax, credits, federal withheld, refund/owed, Schedule C/D/E data

## [0.4.0] - 2026-02-14

### Added

#### Supabase Auth Integration (Backend — Phases 1-3)
- **JWT Authentication**: Supabase JWT validation with HS256, audience verification, expiry checks
- **Auth Dependencies**: `require_auth`, `optional_auth`, `get_current_user` — all in `app/dependencies.py`
- **Backward Compatibility**: When no `TAXLENS_SUPABASE_JWT_SECRET` is set, falls back to anonymous mode (MVP still works)
- **User Management Endpoints**:
  - `GET /api/users/me` — get or auto-create user profile
  - `PATCH /api/users/me` — update profile (name, email)
  - `DELETE /api/users/me` — delete user and ALL associated data (CCPA compliance)
  - `GET /api/users/me/sessions` — session info (managed by Supabase)
  - `GET /api/users/me/audit-log` — user's audit trail
- **Route Protection**: Protected endpoints (documents, accounts, scenarios save, alerts profile, advisor) require auth; public endpoints (health, calculate, alert check, scenario types/run) remain open
- **Data Isolation**: All DB queries scoped by `user_id`; added `user_id` column to Scenario, Alert, EquityGrant models
- **Audit Logging**: `AuditLog` model tracks login, profile updates, document uploads, Plaid links, account deletions with IP address
- **Security Headers Middleware**: CSP, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy
- **Rate Limiting**: `slowapi` integrated for rate limiting support
- **74 tests passing** including auth flows, user CRUD, data isolation, security headers

#### Flutter Frontend — Auth Screens & UX
- **Login Screen** (`login_screen.dart`): Email/password sign-in, Google OAuth, Apple Sign-In, magic link option
- **Signup Screen** (`signup_screen.dart`): New account creation with email/password
- **MFA Setup Screen** (`mfa_setup_screen.dart`): TOTP enrollment, QR code display, verification flow
- **Profile Screen** (`profile_screen.dart`): View/edit user profile, display name, email
- **Account Settings Screen** (`account_settings_screen.dart`): Change email, change password, MFA management, delete account
- **Reauth Dialog** (`reauth_dialog.dart`): Re-authentication prompt for sensitive operations
- **Auth Gate Bottom Sheet** (`auth_gate_bottom_sheet.dart`): Login/signup prompt for unauthenticated users accessing protected features
- **Auth Provider** (`auth_provider.dart`): Riverpod providers for auth state, current user, session, with full OAuth redirect handling (web vs native)

#### Google OAuth Configuration
- Created Google Cloud project `TaxLens-Supabase-Auth`
- Configured OAuth consent screen and credentials
- Integrated with Supabase Google auth provider
- Web redirect configured for `taxlens.ziziou.com`

#### Apple Sign-In Configuration
- Apple Services ID: `com.ziziou.taxlens.web`
- Configured Apple Developer account with Sign In with Apple capability
- Shared key ID `587FQRF28S` with proper domain verification
- Integrated with Supabase Apple auth provider

#### Supabase Project Provisioning
- Project ref: `kccgncphhzodneomimzt`
- URL: `https://kccgncphhzodneomimzt.supabase.co`
- Auth providers enabled: Google, Apple, Email/Password
- Row Level Security configured for data isolation

#### Database Migration: SQLite → Supabase Postgres
- Migrated from local SQLite to Supabase-hosted Postgres
- All models updated for Postgres compatibility
- Backend connects to Supabase Postgres via environment variables

#### Production Deployment to `taxlens.ziziou.com`
- **Backend**: Docker container `taxlens-api` on port 8100 with `--network host`
- **Frontend**: Flutter web build served via Python HTTP server on port 8101
- **Reverse Proxy**: Caddy on port 8102 routing `/api/*` → backend (8100), all else → frontend (8101)
- **Cloudflare Tunnel**: Routes `taxlens.ziziou.com` → `localhost:8102`
- **systemd service**: `taxlens-web.service` manages the frontend web server
- Flutter web built with `--dart-define` for Supabase URL and anon key

### Dependencies Added
- `python-jose[cryptography]>=3.3.0` — JWT decoding
- `slowapi>=0.1.9` — rate limiting
- `supabase_flutter` — Flutter Supabase SDK
- `flutter_riverpod` — state management for auth

---

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
- **Quarterly Underwithholding Check**: Year-to-date pace analysis
- **State Nexus Warnings**: Multi-state tax complexity alerts
- **Wash Sale Detection**: 30-day window monitoring
- **Alert Priority System**: IMMEDIATE, THIS_WEEK, THIS_MONTH, PLANNING

#### Phase 5: What-If Tax Scenario Engine
- **WhatIfEngine**: Core scenario comparison engine
- **Scenario Builders**: RSU timing, ISO exercise, bonus timing, state move, capital gains timing
- **Analysis Functions**: Marginal tax impact, optimal ISO exercise, optimization recommendations

#### Phase 6: Polish & Tests
- Integration tests, end-to-end workflow validation
- Test coverage increased from 73% to 85%+

### Fixed
- Corrected function signatures for `calculate_fica`, `calculate_ltcg_tax`, `calculate_niit`
- AMT calculation now returns actual AMT owed (TMT - regular tax)

## [0.1.0] - 2025-01-15

### Added

#### Phase 1: Core Engine
- Federal tax calculator (2025 rules, all 7 brackets, all filing statuses)
- AMT calculator (exemption, phaseout, ISO bargain element)
- FICA calculator (SS + Medicare + Additional Medicare)
- NIIT calculator (3.8% on investment income)
- California state tax (9 brackets, mental health services tax, SDI)

#### Phase 2: Equity Intelligence
- RSU, ISO, NSO, ESPP calculators
- Fidelity and Schwab CSV importers
- Red flags system (underwithholding, AMT triggers, NIIT thresholds)

---

## Version History Summary

| Version | Date       | Highlights |
|---------|------------|------------|
| 0.4.0   | 2026-02-14 | Supabase auth, Flutter frontend with auth screens, Google/Apple OAuth, Postgres migration, production deployment to taxlens.ziziou.com |
| 0.3.0   | 2025-02-12 | NY/WA state tax, multi-state sourcing, cross-validation, FastAPI backend |
| 0.2.0   | 2025-02-01 | Data integration, enhanced red flags, what-if engine |
| 0.1.0   | 2025-01-15 | Core engine, equity calculations, basic red flags |

## Coming Soon

### v0.5.0 (Planned)
- Plaid integration for automatic data import (stubs exist)
- Real-time stock price fetching
- Tax loss harvesting suggestions
- Document OCR (W-2, 1099 via Claude Vision)
- AI tax advisor (Claude API)

### v1.0.0 (Future)
- Production-ready release
- Security audit complete
- Public beta launch
- Native iOS/Android apps
