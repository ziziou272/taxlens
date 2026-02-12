# TaxLens 🔍

**AI-Powered Tax Intelligence for High-Income Tech Professionals**

> Year-round proactive tax planning, not just annual filing.

## What is TaxLens?

TaxLens is a **tax planning tool** (not a tax filing tool) designed for tech employees with equity compensation ($200K–$1M+). It helps you:

- **Avoid surprises** – Detect underwithholding before April hits
- **Optimize equity** – RSU/ISO/NSO/ESPP timing and strategies
- **Plan ahead** – What-if scenarios for major decisions
- **Stay alert** – 73+ automated tax red flags

## ✅ Current Status

### Engine (v0.2.0+)
- Federal tax calculator (2025 rules, all brackets, AMT, FICA, NIIT, LTCG)
- State tax: California, New York (+ NYC + Yonkers), Washington (capital gains)
- Multi-state sourcing (183-day rule, RSU allocation, part-year moves)
- Equity compensation: RSU, ISO, NSO, ESPP
- Data importers: Fidelity, Schwab, E\*Trade, Robinhood CSV
- 73+ automated red flag alerts
- What-if scenario engine (23 scenario types)
- Cross-validated against IRS reference values (20 scenarios, 0 discrepancies)
- 520+ tests, 82%+ coverage

### API (v0.1.0)
- FastAPI backend with 11+ endpoints
- Tax calculation, alerts, what-if scenarios
- SQLAlchemy async + SQLite
- Pydantic v2 request/response schemas

### Coming Soon
- Flutter cross-platform app (iOS + Android + Web)
- Plaid financial data integration
- Document OCR (W-2, 1099 via Claude Vision)
- AI tax advisor (Claude API)

## Architecture

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
│  │       └────────────┴────────────┴────────────┘              │   │
│  │                    State Management (Riverpod)               │   │
│  │                    Local Cache (Drift/SQLite)                │   │
│  └────────────────────────────┬────────────────────────────────┘   │
│                               │ HTTPS                               │
│  ┌────────────────────────────┼────────────────────────────────┐   │
│  │                      PYTHON BACKEND                          │   │
│  │                            │                                 │   │
│  │           ┌────────────────┴────────────────┐                │   │
│  │           │       FastAPI Application       │                │   │
│  │           │  /api/tax  /api/alerts           │                │   │
│  │           │  /api/scenarios  /api/advisor    │                │   │
│  │           └────────────────┬────────────────┘                │   │
│  │                            │                                 │   │
│  │     ┌──────────┬───────────┼───────────┬──────────┐          │   │
│  │     │ Tax      │ Alert     │ What-If   │ Doc      │          │   │
│  │     │ Engine   │ Engine    │ Engine    │ Extract  │          │   │
│  │     └──────────┘───────────┘───────────┘──────────┘          │   │
│  │                            │                                 │   │
│  │              Database (SQLite → Supabase)                    │   │
│  └────────────────────────────┼────────────────────────────────┘   │
│                               │                                     │
│  ┌────────────────────────────┼────────────────────────────────┐   │
│  │                    EXTERNAL SERVICES                         │   │
│  │     ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐       │   │
│  │     │ Plaid  │  │ Claude │  │ Supabase │  │ Sentry │       │   │
│  │     │  API   │  │  API   │  │  (opt)   │  │ (opt)  │       │   │
│  │     └────────┘  └────────┘  └──────────┘  └────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** AI does NOT do calculations. The calculation engine is 100% deterministic rules. AI only explains, summarizes, and suggests.

## Quick Start

### Engine CLI
```bash
cd packages/engine
pip install -e ".[dev]"
taxlens calculate --income 300000 --filing-status single --state CA
```

### API Server
```bash
cd packages/api
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8100
# Docs at http://localhost:8100/docs
```

## Project Structure

```
taxlens/
├── packages/
│   ├── engine/          # Python tax calculation engine
│   │   ├── taxlens_engine/
│   │   │   ├── federal.py
│   │   │   ├── california.py
│   │   │   ├── new_york.py
│   │   │   ├── washington.py
│   │   │   ├── multi_state.py
│   │   │   ├── equity_*.py
│   │   │   ├── red_flags*.py
│   │   │   ├── what_if.py
│   │   │   └── importers/
│   │   └── tests/
│   └── api/             # FastAPI backend
│       ├── app/
│       │   ├── routers/
│       │   ├── services/
│       │   ├── models/
│       │   └── schemas/
│       └── tests/
├── docs/
├── CHANGELOG.md
├── DECISIONS.md
└── ROADMAP.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Engine | Python 3.11+, Decimal arithmetic |
| API | FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Frontend | Flutter 3.x (coming) |
| Database | SQLite → Supabase |
| AI | Claude API (explanations + OCR) |
| Data | Plaid (financial aggregation) |

## ⚠️ Strategic Decision: Planning First, Filing Later

TaxLens is a **planning tool**, not a filing tool. Filing brings IRS certification, liability for errors, and endless maintenance. Planning is low-risk, high-value, and fills a real market gap — no good equity-focused planning tools exist today.

**Bottom line:** Use TaxLens for planning, TurboTax/CPA for filing. Maybe add filing in v2+ after engine is proven.

## License

MIT

---

**Disclaimer:** TaxLens is a planning tool, not tax advice. Always consult a CPA for filing.
