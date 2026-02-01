# TaxLens Roadmap

## 🎯 2026 Q1: MVP - Core Planning Engine

### Milestone 1: Federal Calculator (2 weeks)

**Goal:** Calculate federal income tax for a W-2 employee with RSUs.

```
Week 1:
├── Set up Python project structure
├── Implement 2025 federal tax brackets
├── Standard deduction logic
├── Basic W-2 income handling
└── Write comprehensive tests

Week 2:
├── AMT calculation engine
├── Long-term capital gains rates
├── Short-term capital gains (ordinary income)
├── RSU income integration
└── Test against TurboTax scenarios
```

**Deliverable:** CLI tool that calculates federal tax for simple equity scenarios.

```bash
$ taxlens calculate \
    --income 300000 \
    --rsu-vested 150000 \
    --rsu-sold 50000 \
    --sale-gain 20000 \
    --filing-status married_jointly

Federal Tax Summary (2025)
─────────────────────────────
Gross Income:        $450,000
RSU Income:          $150,000
Capital Gains (LT):   $20,000
─────────────────────────────
Taxable Income:      $420,000
Federal Tax:         $102,347
Effective Rate:         22.7%
Marginal Rate:           35%
─────────────────────────────
AMT Check:            No AMT triggered
```

### Milestone 2: California State Tax (1 week)

**Goal:** Add CA state tax calculations.

```
Week 3:
├── CA tax brackets (9.3% - 13.3%)
├── CA standard deduction
├── CA SDI/UI considerations
├── Mental health services tax (1% > $1M)
└── Integration tests
```

### Milestone 3: Equity Module (2 weeks)

**Goal:** Handle RSU, ISO, NSO, ESPP with proper tax treatment.

```
Week 4:
├── RSU vesting income (W-2, supplemental withholding)
├── RSU sale (cost basis = FMV at vest)
├── ISO exercise (no regular tax, triggers AMT)
├── ISO disqualifying disposition
└── Test common scenarios

Week 5:
├── NSO exercise (bargain element = ordinary income)
├── NSO sale (cost basis = exercise price + bargain)
├── ESPP purchase (no tax at purchase if qualified)
├── ESPP sale (qualified vs disqualifying)
└── Multi-company scenarios
```

### Milestone 4: Data Import (2 weeks)

**Goal:** Import actual brokerage data.

```
Week 6:
├── Fidelity CSV parser (W-2, 1099-B)
├── Schwab CSV parser
├── E*Trade CSV parser
├── Validate against sample data
└── Error handling & warnings

Week 7:
├── Plaid integration (optional)
├── Manual entry forms
├── Data reconciliation view
└── "Import from TurboTax" export
```

### Milestone 5: Basic Web UI (2 weeks)

**Goal:** Simple web interface for the engine.

```
Week 8:
├── Next.js project setup
├── Dashboard layout
├── Data entry forms
├── Tax summary view
└── Basic styling (Tailwind)

Week 9:
├── File upload for CSV
├── Tax breakdown visualization
├── Year-over-year comparison
├── Mobile responsive
└── Deploy to Vercel
```

**Q1 Deliverable:** Working web app that imports brokerage data and shows tax projections.

---

## 🚨 2026 Q2: Red Flag System

### Milestone 6: Underwithholding Alerts (2 weeks)

```
├── Compare YTD withholding vs projected liability
├── "You're $X short" alert
├── Estimated payment calculator
├── Safe harbor calculation (110% of prior year)
└── Quarterly payment reminders
```

### Milestone 7: AMT Alerts (1 week)

```
├── Detect ISO exercises that trigger AMT
├── Calculate AMT exposure
├── "If you exercise X more ISOs, AMT triggers"
├── AMT credit carryforward tracking
└── Optimization suggestions
```

### Milestone 8: Capital Gains Alerts (1 week)

```
├── WA 7% threshold tracking ($270K in 2025)
├── Short-term vs long-term optimization
├── "Hold X more days for LTCG treatment"
├── Tax-loss harvesting opportunities
└── Wash sale warnings
```

### Milestone 9: Multi-State Alerts (2 weeks)

```
├── Remote work source income tracking
├── "You worked X days in state Y"
├── Multi-state filing requirements
├── Estimated payments by state
└── Moving scenarios
```

---

## 📊 2026 Q3: What-If Engine

### Milestone 10: Interactive Scenarios (3 weeks)

```
├── Slider-based income adjustments
├── "What if I exercise X ISOs this year vs next?"
├── "What if I sell RSUs now vs after LTCG?"
├── Roth conversion optimizer
├── Retirement contribution optimizer (401k, IRA, backdoor)
```

### Milestone 11: Year-End Planning Mode (2 weeks)

```
├── October-December planning view
├── Checklist of year-end moves
├── Deadline reminders
├── "Last chance to..." alerts
├── Next year projections
```

### Milestone 12: AI Explanations (2 weeks)

```
├── Claude API integration
├── "Explain my tax situation"
├── "What does AMT mean for me?"
├── Strategy summaries in plain English
├── Personalized recommendations
```

---

## 🚀 2026 Q4: Polish & Growth

### Milestone 13: Beta Launch (4 weeks)

```
├── Security audit
├── Performance optimization
├── Error monitoring (Sentry)
├── Analytics (privacy-respecting)
├── Invite beta testers (20-50 users)
```

### Milestone 14: Public Launch (4 weeks)

```
├── Landing page
├── Pricing page ($99/year or $299/year premium)
├── Stripe integration
├── Onboarding flow
├── Help docs & FAQ
```

---

## 🔮 Future (2027+)

### Maybe: Tax Filing

Once the calculation engine is battle-tested with real users:
- Research IRS e-file certification
- Partner with existing filing provider?
- Or stay in planning lane (less liability)

### Multi-State Full Support

- All 50 states
- International (UK, Canada, etc.)
- Expat scenarios

### Business/1099 Support

- Freelancer income
- Estimated quarterly payments
- Business deductions

### Team/Family

- Shared household view
- Tax preparer mode
- Multi-user access

---

## 📈 Success Metrics

| Metric | Q1 Target | Q2 Target | Q4 Target |
|--------|-----------|-----------|-----------|
| Calculation accuracy | 95% | 99% | 99.9% |
| Active users | 10 (friends) | 100 (beta) | 1000 (launch) |
| NPS | N/A | 50+ | 60+ |
| Alerts triggered | N/A | 500+ | 5000+ |
| Tax savings identified | N/A | $50K+ | $500K+ |
