# TaxLens Roadmap

## ✅ Completed

### Engine v0.1.0 – Core Engine (Jan 2025)
- [x] Federal tax calculator (2025 brackets, all filing statuses)
- [x] AMT calculation engine
- [x] FICA (SS + Medicare + Additional Medicare)
- [x] NIIT (Net Investment Income Tax)
- [x] LTCG preferential rates
- [x] California state tax (9 brackets + mental health services tax)
- [x] Equity modules: RSU, ISO, NSO, ESPP
- [x] Data importers: Fidelity, Schwab CSV
- [x] Basic red flag system

### Engine v0.2.0 – Data Integration & What-If (Feb 2025)
- [x] E\*Trade CSV importer
- [x] Robinhood CSV importer
- [x] Manual entry data models
- [x] Enhanced red flags: estimated payments, wash sales, state nexus
- [x] What-if scenario engine (23 scenario types)
- [x] Integration tests

### Engine v0.3.0 – Multi-State & Validation (Feb 2025)
- [x] Washington state capital gains tax (PR #13)
- [x] New York state tax + NYC + Yonkers (PR #14)
- [x] Cross-validation suite: 20 scenarios, 0 discrepancies (PR #15)
- [x] Multi-state income sourcing: 183-day rule, RSU allocation (PR #16)
- [x] FastAPI backend with 11+ endpoints (PR #17)
- [x] 520+ tests, 82%+ coverage

---

## 🚧 In Progress

### 2025 Q1: Flutter App MVP
- [ ] Flutter project setup (Riverpod, go_router)
- [ ] Dashboard screen – tax summary overview
- [ ] Data entry forms – W-2, equity grants
- [ ] Tax breakdown visualization
- [ ] Alerts list view
- [ ] What-if scenario UI with sliders

### 2025 Q1: API Enhancements
- [ ] User authentication (Supabase Auth)
- [ ] Persistent user profiles
- [ ] Document upload endpoint

---

## 📋 Planned

### 2025 Q2: Data & Intelligence
- [ ] Plaid integration for automatic brokerage data import
- [ ] Document OCR: W-2, 1099-B via Claude Vision
- [ ] AI tax advisor: Claude API for plain-English explanations
- [ ] Real-time stock price fetching
- [ ] Tax-loss harvesting suggestions

### 2025 Q3: Polish & Beta
- [ ] Year-end planning mode (Oct–Dec checklist)
- [ ] Security audit
- [ ] Performance optimization
- [ ] Beta launch (20–50 users)

### 2025 Q4: Public Launch
- [ ] Landing page & onboarding flow
- [ ] Stripe billing ($99/yr or $299/yr premium)
- [ ] Help docs & FAQ
- [ ] Public launch

---

## 🔮 Future (2026+)

- **Tax filing** – Once engine is battle-tested, explore IRS e-file certification
- **All 50 states** – Full multi-state coverage
- **International** – UK, Canada, expat scenarios
- **Business/1099** – Freelancer income, business deductions
- **Team/Family** – Shared household view, tax preparer mode

---

## 📈 Success Metrics

| Metric | Current | Q2 Target | Launch Target |
|--------|---------|-----------|---------------|
| Calculation accuracy | 99.9%+ (cross-validated) | 99.9% | 99.99% |
| Test coverage | 82%+ | 90% | 95% |
| Active users | — | 100 (beta) | 1,000 |
| Alerts available | 73+ | 100+ | 150+ |
| States supported | 3 (CA, NY, WA) | 5+ | 15+ |
