# TaxLens 🔍

**AI-Powered Tax Intelligence for High-Income Tech Professionals**

> Year-round proactive tax planning, not just annual filing.

## 🎯 What is TaxLens?

TaxLens is a **tax planning tool** (not a tax filing tool) designed for tech employees with equity compensation ($200K-$1M+). It helps you:

- **Avoid surprises** - Detect underwithholding before April hits
- **Optimize equity** - RSU/ISO/NSO/ESPP timing and strategies
- **Plan ahead** - What-if scenarios for major decisions
- **Stay alert** - 73+ automated tax red flags

## ⚠️ Strategic Decision: Planning First, Filing Later

### Why NOT build a filing tool (yet)?

| Risk | Impact |
|------|--------|
| IRS e-file certification | Complex, expensive process |
| Liability for errors | One mistake = thousands in penalties |
| Annual tax code changes | Endless maintenance burden |
| Multi-state complexity | 50 states × changing rules |

### Why Planning is the Sweet Spot

1. **Low risk** - Projections don't file anything
2. **High value** - TurboTax sucks at year-round planning
3. **Validates engine** - Battle-test calculations before filing
4. **Market gap** - No good equity-focused planning tools exist

**Bottom line:** Use TaxLens for planning, TurboTax/CPA for filing. Maybe add filing in v2+ after engine is proven.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TaxLens Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐     ┌────────────────────────────────┐│
│  │   AI Layer       │     │   Calculation Engine           ││
│  │   (Claude API)   │     │   (Deterministic Rules)        ││
│  │                  │     │                                ││
│  │   • Q&A          │     │   • Federal tax brackets       ││
│  │   • Explanations │     │   • AMT calculations           ││
│  │   • Strategies   │     │   • State tax rules            ││
│  │   • Summaries    │     │   • Equity comp (RSU/ISO/NSO)  ││
│  │                  │     │   • Capital gains              ││
│  └────────┬─────────┘     └──────────────┬─────────────────┘│
│           │                              │                   │
│           └──────────────┬───────────────┘                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │     TaxLens App       │                       │
│              │  • Dashboard          │                       │
│              │  • Red Flag Alerts    │                       │
│              │  • What-If Scenarios  │                       │
│              │  • Data Import        │                       │
│              └───────────────────────┘                       │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │   Data Sources        │                       │
│              │  • Fidelity/Schwab    │                       │
│              │  • Plaid (bank link)  │                       │
│              │  • Manual entry       │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** AI does NOT do calculations. The calculation engine is 100% deterministic rules. AI only explains, summarizes, and suggests.

## 📋 Implementation Phases

### Phase 1: Core Engine (Weeks 1-4)
- [ ] Federal tax bracket calculator (2025 rules)
- [ ] AMT calculation engine
- [ ] California state tax
- [ ] Basic W-2 + RSU scenario

### Phase 2: Equity Intelligence (Weeks 5-8)
- [ ] RSU vesting projections
- [ ] ISO exercise + AMT interaction
- [ ] NSO exercise timing
- [ ] ESPP disposition analysis

### Phase 3: Data Integration (Weeks 9-12)
- [ ] Fidelity CSV import
- [ ] Schwab CSV import
- [ ] Plaid connection (optional)
- [ ] Manual entry forms

### Phase 4: Red Flag System (Weeks 13-16)
- [ ] Underwithholding alerts
- [ ] AMT trigger warnings
- [ ] WA capital gains threshold
- [ ] Wash sale detection

### Phase 5: What-If Engine (Weeks 17-20)
- [ ] Interactive sliders
- [ ] Scenario comparison
- [ ] Tax optimization suggestions
- [ ] Year-end planning mode

### Phase 6: Polish & Launch (Weeks 21-24)
- [ ] UI/UX refinement
- [ ] Security audit
- [ ] Beta testing
- [ ] Public launch

## 🛠️ Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js + Tailwind | Modern React, great DX |
| **Backend** | Python (FastAPI) | Tax-Calculator is Python, easy integration |
| **Database** | PostgreSQL + Supabase | Secure, scalable |
| **AI** | Claude API | Best for explanations, uses their API |
| **Calculations** | Python (Decimal) | Exact arithmetic, no floating point errors |
| **Data Import** | Plaid + CSV parsers | Cover all brokerages |

## 📁 Project Structure

```
taxlens/
├── README.md
├── DECISIONS.md          # Architecture Decision Records
├── docs/
│   ├── research/         # Existing research from aiOutput
│   ├── specs/            # Technical specifications
│   └── api/              # API documentation
├── packages/
│   ├── engine/           # Tax calculation engine (Python)
│   ├── web/              # Next.js frontend
│   └── shared/           # Shared types/utils
├── scripts/
│   └── tax-data/         # IRS data scrapers
└── tests/
    ├── engine/           # Calculation tests
    └── integration/      # End-to-end tests
```

## 🚀 Getting Started

```bash
# Clone
git clone https://github.com/ziziou272/taxlens.git
cd taxlens

# Install engine dependencies
cd packages/engine
pip install -e .

# Run tests
pytest

# Start dev server
cd ../web
npm install
npm run dev
```

## 📊 Key Metrics for Success

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Calculation accuracy | 99.99% | Compare vs TurboTax/CPA results |
| False positive alerts | <5% | User feedback on red flags |
| User time saved | 10+ hrs/year | Survey + analytics |
| Tax savings identified | $1000+/user | Track what-if suggestions |

## 🔒 Security & Privacy

- All financial data encrypted at rest (AES-256)
- No data sold or shared
- SOC 2 compliance (future)
- User can export/delete all data

## 📚 Research & Prior Art

See `/docs/research/` for comprehensive research including:
- Competitor analysis (TurboTax, H&R Block, etc.)
- Open source options (PSLmodels/Tax-Calculator)
- AI/LLM limitations for tax calculations
- Academic papers on tax optimization

## 📜 License

MIT (engine) + Proprietary (future commercial features)

## 🤝 Contributing

This is currently a personal project. Contributions welcome after initial MVP.

---

**Disclaimer:** TaxLens is a planning tool, not tax advice. Always consult a CPA for filing. We are not responsible for any tax decisions made based on this tool.
