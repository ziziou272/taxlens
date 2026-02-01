# Task 1: Existing Solutions & Prior Art - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document catalogs existing AI models, open-source tools, APIs, and competitor approaches for tax calculation and financial planning. Key findings:

1. **No production-ready AI model exists for accurate tax calculations** - Financial LLMs excel at sentiment analysis and text understanding, not numerical tax computations
2. **Best approach: Use Claude/GPT for explanations + deterministic engine for calculations** (Intuit's proven model)
3. **Strong open-source tax calculators exist** (PSLmodels/Tax-Calculator) that can be leveraged
4. **Competitors use proprietary rules engines** - AI is for UX/explanations, not core calculations

---

## 1. AI Models & LLMs for Finance/Tax

### 1.1 Finance-Specific LLMs

| Model | Provider | Capabilities | Access | Relevance for TaxLens |
|-------|----------|--------------|--------|----------------------|
| **BloombergGPT** | Bloomberg | 50B params, financial NLP, sentiment analysis, entity recognition | Proprietary (Bloomberg Terminal only) | LOW - Not accessible, focused on market data |
| **FinGPT** | Open Source (AI4Finance) | Sentiment analysis, financial NLP, fine-tunable | Open source, GitHub | MEDIUM - Could be base for fine-tuning, but not tax-focused |
| **FinBERT** | Open Source | Financial sentiment classification | Hugging Face | LOW - NLP only, not calculations |
| **InvestLM** | Open Source | Investment advice, LLaMA-65B fine-tuned | Open source | LOW - Investment focus, not tax |
| **FinLlama** | Open Source | Financial sentiment classification | Hugging Face | LOW - Classification only |

### 1.2 Key Insight: AI Models Cannot Calculate Taxes

**Critical Finding:** All finance-specific LLMs are optimized for:
- Sentiment analysis
- Named entity recognition
- Text classification
- Question answering about finance concepts

**None are designed for numerical tax calculations.** The reason: Tax calculations require:
- Deterministic rules (tax brackets, thresholds)
- Exact arithmetic
- Complex conditional logic (AMT, phase-outs)
- State-specific rules

LLMs are probabilistic and prone to calculation errors ("hallucinations").

### 1.3 How Competitors Use AI (The Right Way)

**Intuit/TurboTax Approach (RECOMMENDED MODEL):**
```
┌─────────────────────────────────────────────────────────────┐
│                    INTUIT ARCHITECTURE                      │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐│
│  │ Claude (via     │    │ Proprietary Tax Knowledge Engine││
│  │ Amazon Bedrock) │    │ - 15,000+ tax forms            ││
│  │                 │    │ - 100,000 pages of tax code    ││
│  │ Used for:       │    │ - Rules-based calculations     ││
│  │ - Explanations  │    │                                 ││
│  │ - Q&A           │    │ Used for:                       ││
│  │ - Contextual    │    │ - ALL calculations              ││
│  │   guidance      │    │ - Bracket math                  ││
│  │                 │    │ - Deduction logic               ││
│  └────────┬────────┘    └───────────────┬─────────────────┘│
│           │                             │                   │
│           └──────────────┬──────────────┘                   │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │    Intuit Assist      │                      │
│              │ (User-facing product) │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

**Key Quote from AARP article:**
> "What generative AI doesn't do well yet is math. So Intuit is not using the AI for calculations, in part to avoid those hallucinations."

**H&R Block Approach:**
- Built on Azure OpenAI Service (GPT-based)
- AI Tax Assist answers questions using curated content from H&R Block Tax Institute
- Does NOT perform calculations - only explains and guides
- Trained on proprietary tax knowledge, not general internet

---

## 2. Open Source Tax Calculators

### 2.1 Recommended: PSLmodels/Tax-Calculator

| Attribute | Value |
|-----------|-------|
| **Repository** | https://github.com/PSLmodels/Tax-Calculator |
| **Language** | Python |
| **Stars** | 289 |
| **Last Updated** | December 2025 (Release 6.3.0) |
| **License** | Open Source |
| **Coverage** | Federal income tax, payroll taxes |
| **Maintenance** | Actively maintained, seeking contributors |

**Features:**
- Microsimulation model for USA federal income and payroll taxes
- 200+ parameters that can be changed without programming
- Marginal tax rate calculations for 18 income types
- Tax reform simulation capabilities
- Well-documented API

**Assessment:**
- ✅ Actively maintained
- ✅ Comprehensive federal coverage
- ✅ Python-based (matches our stack)
- ✅ Well-tested
- ⚠️ No state tax support
- ⚠️ No equity compensation handling
- ⚠️ Designed for policy analysis, not consumer apps

### 2.2 Other Open Source Options

| Project | URL | Assessment |
|---------|-----|------------|
| **tenforty** | github.com/mmacpherson/tenforty | Python wrapper for Open Tax Solver. Good for form calculations. ChatGPT integration available. |
| **habutax** | github.com/habutax/habutax | Personal tax solver. US 1040 focus. Python. |
| **python-taxes** | github.com/stacynoland/python-taxes | Social Security, Medicare, Federal income. 2023-2025 support. Simple API. |
| **py1040** | github.com/b-k/py1040 | Single 1040 calculator. Good for verification. |

### 2.3 Recommendation

**Build custom + leverage Tax-Calculator:**
- Use Tax-Calculator as reference/validation for federal calculations
- Build custom engine for:
  - Equity compensation (RSU, ISO, NSO, ESPP)
  - State taxes (CA, NY)
  - AMT calculations
  - Real-time projections
  - What-if scenarios

---

## 3. Competitor Analysis

### 3.1 TurboTax / Intuit

**Technology Stack:**
- **Intuit Assist**: GenAI assistant built on "GenOS" (proprietary AI operating system)
- **Amazon Bedrock + Claude**: Powers explanations and Q&A
- **Proprietary Tax Engine**: 40+ years of tax rules, deterministic calculations
- **Document AI**: Automated data entry for 90% of common forms
- **60 billion ML predictions daily** across platform

**Key Capabilities:**
- Real-time accuracy checks
- Contextual explanations of calculations
- Expert matching via ML
- Automated form import from 350+ financial institutions

**What We Can Learn:**
1. AI for UX, not calculations
2. Proprietary knowledge base is critical
3. Confidence comes from guarantees + human backup

### 3.2 H&R Block

**Technology Stack:**
- **Azure OpenAI Service**: GPT-based AI Tax Assist
- **H&R Block Tax Institute**: Proprietary knowledge base from 70 years of expertise
- **Microsoft Partnership**: Deep integration with Azure

**Key Features:**
- AI Tax Assist available in Deluxe+ packages
- Answers tax questions using vetted content
- Does NOT pull from internet - only curated content
- Human expert backup always available
- 100% accuracy guarantee

**Architecture Insight:**
> "If we're doing our jobs right and we don't have the right content or a complete picture of that content, we've got to go, 'Sorry, I'm not trained on that content yet.'" - H&R Block

### 3.3 Range (AI-First Wealth Management)

**Technology Stack:**
- **Proprietary AI (Rai)**: CFP-trained financial AI
- **Custom Financial Planning Tool**: Built from scratch, not third-party
- **Custom Tax Planning Engine**: Replaced industry-standard tools
- **Monte Carlo Simulations**: Retirement modeling

**Key Capabilities:**
- 98% accuracy on financial certification exams (vs 72% human average)
- Plans delivered in seconds vs days/weeks
- Comprehensive scenario modeling (ISO exercise + rental property + Roth conversion)
- $4,800-$8,955/year pricing

**What We Can Learn:**
1. Speed of outcome is key differentiator
2. Build proprietary tools for control and speed
3. AI + human hybrid model for trust
4. Specific focus on high-income tech professionals

### 3.4 Holistiplan

**Technology Stack:**
- **OCR Technology**: Scans tax returns, extracts data in 45 seconds
- **Scenario Modeling**: Roth conversions, QCDs, equity comp
- **Multi-year Projections**: Tax impact over time

**Key Features:**
- #1 Tax Planning Software (2021-2025 per Kitces Report)
- Upload 1040 → instant analysis
- No manual data entry required
- Integrates with eMoney, RightCapital

**Pricing:** $160+/month (for advisors)

**What We Can Learn:**
1. OCR for document processing is proven
2. Advisor-facing tools have different needs than consumer
3. Scenario comparison is high-value feature

### 3.5 Betterment (Tax-Loss Harvesting)

**Algorithm Approach:**
- Daily scanning for harvesting opportunities
- Parallel securities (primary + alternate ETFs)
- Wash sale avoidance algorithm
- Options theory for harvest thresholds
- Cost basis lot-level tracking

**Key Metrics:**
- Harvested ~$60M in losses during Spring 2025 volatility
- 70% of TLH users had advisory fee covered by tax savings
- Average 1.94% annual tax offset

**Harvest Threshold Rule (from SSRN paper):**
- -10% threshold for monthly harvesting
- -15% threshold for daily harvesting
- Based on wash sale lockout opportunity cost

**What We Can Learn:**
1. Daily automated scanning is feasible
2. Parallel securities strategy avoids wash sales
3. Quantifiable value proposition (% tax savings)

---

## 4. Academic Papers & Research

### 4.1 Tax-Loss Harvesting

| Paper | Key Finding |
|-------|-------------|
| "Optimized Tax Loss Harvesting" (SSRN 4152425) | -10% monthly / -15% daily threshold is robust across settings |
| Vanguard TLH Research | XGBoost ML used to predict TLH value; personalization matters |
| Betterment NYU Paper | Options theory framework: harvest when value > 30-day put option value |

### 4.2 Key Academic Insights

1. **Wash Sale Rule Creates Optimization Problem:**
   - 30-day window constraint
   - Substantially identical security definition matters
   - Cross-account (taxable ↔ IRA) issues

2. **TLH Value Depends On:**
   - Investor's tax rate
   - Market volatility
   - Time horizon
   - Available replacement securities

3. **Algorithmic Approach:**
   ```
   for each holding in portfolio:
       if loss > threshold AND not in wash_sale_lockout:
           harvest_loss(holding)
           buy_replacement_security()
           set_lockout(holding, 30_days)
   ```

---

## 5. Tax Calculation APIs & Services

### 5.1 Plaid Investment API

**Available Data:**
| Field | Available | Notes |
|-------|-----------|-------|
| Holdings | ✅ | account_id, quantity, security_id, institution_value |
| Cost Basis | ✅ | Per holding |
| Transactions | ✅ | 24 months history |
| Security Type | ✅ | stock, ETF, mutual fund, etc. |
| Dividends | ✅ | Via transaction type |
| Vesting Events | ❌ | Not directly available |
| RSU/ISO Grants | ❌ | Not available |

**Coverage:**
- Banks, brokerages, crypto exchanges
- Retirement accounts (401k, IRA, Roth)
- 529, HSA, UGMA/UTMA
- Nearly 20 account types

**Limitations:**
- No equity compensation grant details
- No vesting schedule data
- Cost basis may be missing for older positions
- No W-2 or tax document access

### 5.2 Data Gap Analysis

| Data Needed | Plaid | Manual Input |
|-------------|-------|--------------|
| Holdings & values | ✅ | - |
| Cost basis | Partial | ✅ for missing |
| RSU grant details | ❌ | ✅ Required |
| ISO exercise history | ❌ | ✅ Required |
| W-2 income | ❌ | ✅ Required |
| Filing status | ❌ | ✅ Required |
| State of residence | ❌ | ✅ Required |
| Vesting schedule | ❌ | ✅ Required |

---

## 6. Recommendations

### 6.1 AI Strategy

**Recommended Approach:**
```
┌─────────────────────────────────────────────────────────────┐
│                   TAXLENS ARCHITECTURE                      │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐│
│  │ Claude API      │    │ Custom Tax Engine (Python)      ││
│  │                 │    │                                 ││
│  │ Used for:       │    │ - Federal tax brackets         ││
│  │ - Explanations  │    │ - State tax calculations       ││
│  │ - Recommendations│   │ - AMT logic                    ││
│  │ - Q&A           │    │ - Equity comp rules            ││
│  │ - Document OCR  │    │ - NIIT, Medicare surtax        ││
│  │ - Personalized  │    │ - What-if projections          ││
│  │   advice        │    │ - Red flag detection           ││
│  └────────┬────────┘    └───────────────┬─────────────────┘│
│           │                             │                   │
│           └──────────────┬──────────────┘                   │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │    TaxLens App        │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Build vs. Buy

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Tax calculation engine | **BUILD** | Core IP, needs equity comp, state tax |
| Document OCR | **USE CLAUDE** | Vision + structured output proven |
| TLH algorithm | **BUILD** | Follow Betterment/Vanguard research |
| Tax explanations | **USE CLAUDE** | LLMs excel at explanation |
| Data aggregation | **USE PLAID** | Not core differentiator |

### 6.3 Gaps to Fill

1. **Equity compensation rules** - No existing solution handles RSU/ISO/ESPP comprehensively
2. **State tax engines** - Need to build for CA, NY, WA
3. **Multi-year projections** - Novel feature vs competitors
4. **Red flag detection** - Custom alert logic required
5. **What-if scenarios** - Interactive modeling engine needed

---

## 7. Sources

### Financial LLMs
- FinGPT GitHub: https://github.com/AI4Finance-Foundation/FinGPT
- "Survey of LLMs for Financial Applications" (arXiv 2406.11903)
- Turing Institute: "Impact of LLMs in Finance"

### Competitor Technology
- Intuit AWS Blog: Amazon Bedrock + Claude integration
- Microsoft Case Study: H&R Block Azure OpenAI
- Range.com: AI financial advisor features
- Holistiplan.com: Tax planning software

### Open Source Tax Tools
- PSLmodels/Tax-Calculator: https://github.com/PSLmodels/Tax-Calculator
- tenforty: https://github.com/mmacpherson/tenforty
- python-taxes: https://github.com/stacynoland/python-taxes

### Academic Research
- SSRN 4152425: "Optimized Tax Loss Harvesting"
- Vanguard: "Tax-Loss Harvesting: Why a Personalized Approach Is Important"
- NYU/Betterment: "Algorithmic Approach to Taxable Investing"

### APIs
- Plaid Investment API Documentation: https://plaid.com/docs/investments/

---

*Document generated as part of TaxLens Phase 1 Research*
