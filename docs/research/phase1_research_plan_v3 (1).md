# Phase 1: Core Tax Intelligence - AI Research Plan v3.1

## Purpose
This research plan is designed to be executed by AI (Claude or similar). Each section contains specific research questions and instructions for the AI to investigate and document findings.

**v3 Changes:** Expanded Task 6 (Red Flags) from 10 to 65+ alerts covering investment sale timing, wash sales, dividend qualification, ESPP dispositions, life events, threshold proximity, and CA-specific rules.

**v3.1 Changes:** Added Task 9 (User Trust & Data Sensitivity) - researching why users would trust a new app with sensitive financial data and strategies to overcome adoption barriers.

---

## Research Task 1: Existing Solutions & Prior Art

### Objective
Before building anything, find existing models, libraries, papers, and open source projects related to tax calculation and optimization.

### Research Instructions

**1.0 AI Models & LLMs for Finance/Tax**

Search for AI/ML models specifically built or fine-tuned for:
- Tax calculation or tax planning
- Financial planning and advice
- Personal finance optimization
- Equity compensation analysis

**Areas to Research:**

| Category | What to Find |
|----------|--------------|
| **Finance-specific LLMs** | Models fine-tuned on financial data (BloombergGPT, FinGPT, etc.) |
| **Tax-focused AI** | Any models trained specifically for tax scenarios |
| **Financial reasoning models** | Models optimized for numerical/financial calculations |
| **Fintech AI tools** | AI APIs offered by fintech companies |
| **Open source financial models** | Hugging Face models tagged finance/tax |

**Specific Searches:**
- "LLM fine-tuned tax" / "LLM financial planning"
- "BloombergGPT" capabilities and access
- "FinGPT" / "FinBERT" / financial NLP models
- Hugging Face: search for finance, tax, accounting models
- "GPT for tax" / "Claude for financial planning"
- AI tax assistants (Intuit AI, H&R Block AI, etc.)
- "Machine learning tax optimization"
- "AI-powered financial advisor" technology

**For Each Model/Tool Found, Document:**
- Model name and provider
- What it's trained/optimized for
- Capabilities relevant to our use case
- Access method (API, open source, commercial)
- Accuracy/reliability for tax calculations
- Limitations and caveats
- Pricing (if commercial)
- Can it be fine-tuned further?

**Key Questions to Answer:**
1. Is there a model that can already calculate taxes accurately?
2. Can we use an existing financial LLM as a base?
3. What are competitors using for their AI features?
4. Should we fine-tune a model or use prompting?
5. What's the state of AI accuracy for tax advice?

**Also Research:**
- How TurboTax uses AI (Intuit Assist)
- How H&R Block uses AI
- Range's AI capabilities ("30-hour advisor work in 30 minutes")
- Holistiplan's AI/ML features
- Any regulations on AI for tax/financial advice

**1.1 Open Source Tax Calculators**
Search for and evaluate:
- GitHub repositories for tax calculation (Python, JavaScript, any language)
- Open source tax filing software
- Tax bracket calculators with source code
- IRS form calculation implementations

For each found, document:
- Repository URL
- Language/framework
- Features covered
- Last updated (is it maintained?)
- License (can we use it?)
- Code quality assessment

**1.2 Academic Papers & Research**
Search for papers on:
- "Tax optimization algorithms"
- "Personal finance decision modeling"
- "Tax-loss harvesting optimization"
- "Retirement contribution optimization"
- "AMT calculation models"
- "Equity compensation tax planning"
- "Roth conversion optimization models"

Sources to search:
- Google Scholar
- SSRN (Social Science Research Network)
- NBER (National Bureau of Economic Research)
- arXiv (quantitative finance section)

For each relevant paper, document:
- Title, authors, year
- Key findings/methodology
- Applicable insights for our product
- Link/DOI

**1.3 Industry Whitepapers & Essays**
Search for:
- Vanguard research on Roth conversions
- Fidelity tax planning guides
- Kitces.com articles on tax optimization
- Bogleheads wiki tax strategies
- Financial planning journal articles

**1.4 Existing APIs & Services**
Search for:
- Tax calculation APIs (commercial)
- Tax data providers
- IRS e-file APIs or data feeds
- State tax APIs

For each, document:
- Service name and URL
- What it provides
- Pricing model
- API documentation quality
- Limitations

**1.5 How Competitors Built Their Tax Engines**
Research how these companies built their tax features:
- TurboTax / Intuit tax engine
- H&R Block calculation methodology
- Holistiplan technology stack
- Range's tax projection approach
- Betterment's tax-loss harvesting algorithm

Search for:
- Engineering blog posts
- Patent filings
- Job postings (reveal tech stack)
- Conference talks / presentations

### Output Format
Create a document with:
1. Summary table of all resources found
2. Recommended resources to leverage
3. Gaps where we must build custom

---

## Research Task 2: Federal Tax Calculation Engine

### Objective
Document the exact formulas, brackets, and logic needed to calculate federal income tax for high-income individuals.

### Research Instructions

**2.1 Tax Brackets & Rates**
Find and document for 2024 AND 2025:
- Federal tax brackets for all filing statuses (Single, MFJ, MFS, HoH)
- Qualified dividend / LTCG rate thresholds (0%, 15%, 20%)
- Net Investment Income Tax (NIIT) threshold and rate
- Additional Medicare Tax threshold and rate

Source: IRS.gov, Revenue Procedures

**2.2 Tax Calculation Formulas**
Document step-by-step calculation:
1. Gross Income calculation
2. Adjustments to income (above-the-line deductions)
3. AGI calculation
4. Standard vs. Itemized deduction decision
5. Taxable income calculation
6. Tax liability calculation (bracket math)
7. Credits application
8. Additional taxes (NIIT, Medicare)
9. Total tax owed

**2.3 Deduction Rules**
Research and document:
- Standard deduction amounts (2024, 2025)
- SALT cap ($10,000) - rules and exceptions
- Mortgage interest limits
- Charitable contribution AGI limits
- Phase-outs for high earners (if any remain after TCJA)

**2.4 Alternative Minimum Tax (AMT)**
Document:
- AMT exemption amounts by filing status
- AMT phase-out thresholds
- AMT preference items list
- AMT calculation formula
- When AMT exceeds regular tax

**2.5 Tax Withholding Rules**
Research:
- W-4 withholding tables
- Supplemental wage withholding (22% flat rate)
- Over $1M supplemental rate (37%)
- State withholding requirements

### Output Format
Create specification document with:
1. All tax tables (brackets, thresholds)
2. Calculation formulas in pseudocode
3. Decision trees for complex logic (AMT, itemize vs standard)
4. Edge cases and special rules

---

## Research Task 3: Equity Compensation Tax Rules

### Objective
Document the complete tax treatment of RSUs, ISOs, NSOs, and ESPPs with specific focus on high-income scenarios.

### Research Instructions

**3.1 RSU (Restricted Stock Units) Taxation**
Research and document:
- Tax treatment at vesting (ordinary income)
- Federal withholding requirements (22% vs 37% threshold)
- State withholding by state (focus: CA, NY)
- Sell-to-cover mechanics
- Cost basis establishment
- Holding period for subsequent sale
- Common underwithholding calculation

Find: IRS guidance, employer stock plan documentation, tax court cases

**3.2 ISO (Incentive Stock Options) Taxation**
Research and document:
- Tax treatment at grant (none)
- Tax treatment at exercise:
  - Regular tax: none
  - AMT: adjustment = (FMV - strike) × shares
- Qualifying disposition requirements (2yr/1yr holding)
- Disqualifying disposition treatment
- AMT credit carryforward mechanics
- Early exercise considerations (83b election)

Find: IRS Publication 525, Form 6251 instructions, ISO-specific tax guides

**3.3 NSO (Non-Qualified Stock Options) Taxation**
Research and document:
- Tax at exercise (ordinary income on spread)
- Withholding requirements
- Cost basis = FMV at exercise
- Subsequent sale treatment

**3.4 ESPP (Employee Stock Purchase Plan) Taxation**
Research and document:
- Section 423 qualified plan rules
- Qualifying disposition (2yr offering / 1yr purchase)
- Disqualifying disposition treatment
- Ordinary income vs capital gain allocation
- Discount taxation

**3.5 Multi-State Equity Compensation**
Research:
- State sourcing rules for RSU/ISO income
- California's strict sourcing rules
- New York allocation methods
- Remote work complications

### Output Format
Create specification document with:
1. Tax treatment summary table by equity type
2. Calculation formulas for each scenario
3. Withholding rate tables (federal + key states)
4. Decision trees for ISO AMT calculation
5. Cost basis tracking requirements

---

## Research Task 4: State Tax Calculations

### Objective
Document state tax rules for priority states where high-income tech workers live.

### Research Instructions

**4.1 California**
Research and document:
- Income tax brackets (2024, 2025)
- Mental Health Services Tax (1% over $1M)
- SDI rates and caps (changed 2024 - now uncapped)
- No preferential capital gains rate
- State AMT rules (if any)
- Equity compensation sourcing rules

Source: FTB.ca.gov, state tax forms

**4.2 New York**
Research and document:
- State income tax brackets
- New York City income tax brackets
- Combined state + city rates
- SALT cap impact analysis
- Equity compensation sourcing

**4.3 No Income Tax States**
Document for Washington, Texas, Florida, Nevada, Tennessee, Wyoming:
- Any taxes that affect high earners
- Capital gains treatment
- What to show users in these states

**4.4 Multi-State Considerations**
Research:
- How states tax remote workers
- State reciprocity agreements
- RSU vesting in multiple states
- State tax credit for taxes paid to other states

### Output Format
Create specification document with:
1. Tax bracket tables for CA, NY, NYC
2. State-specific rules and exceptions
3. Multi-state allocation examples
4. Comparison table (tax on $500K income by state)

---

## Research Task 5: Data Mapping & Integration

### Objective
Document how to get tax-relevant data from Plaid and other sources, and what must be manually input.

### Research Instructions

**5.1 Plaid Investment API Data**
Research Plaid documentation:
- What data fields are available for holdings?
- Can we identify security type (stock, RSU, option)?
- Transaction data available (buys, sells, dividends)
- Can we detect vesting events?
- Cost basis availability
- Limitations and gaps

Source: Plaid API documentation, developer forums

**5.2 Plaid Transaction Data**
Research:
- Income categorization accuracy
- Payroll/salary detection
- Can we identify employer?
- Tax withholding in transaction data?

**5.3 Brokerage-Specific Data**
Research what additional data is available from:
- Fidelity (NetBenefits for RSUs)
- E*Trade (equity compensation)
- Schwab
- Morgan Stanley (Shareworks)

**5.4 Manual Input Requirements**
Determine what MUST be manually entered:
- Filing status
- Dependents
- Prior year carryforwards
- RSU grant details?
- ISO exercise history?
- Other income sources

**5.5 Data Accuracy & Confidence**
Research:
- How accurate is Plaid investment data?
- Common data quality issues
- How to handle missing/incomplete data
- When to ask user to verify

### Output Format
Create specification document with:
1. Plaid data field inventory (what's available)
2. Mapping table: Plaid field → Tax input
3. Required manual inputs list
4. Data quality handling rules
5. Gaps and workarounds

## Research Task 6: Red Flag Dashboard

### Objective
Research and specify the detection logic for proactive tax optimization alerts covering ALL tax-impacting events.

### Research Instructions

**6.1 Research Common Tax Mistakes**
Search for:
- "Common tax mistakes high income" 
- "Tax planning errors" articles
- CPA blogs on client mistakes
- Reddit r/tax, r/personalfinance mistake threads
- TurboTax audit alerts (what do they check?)

Document top 20 mistakes with frequency and dollar impact.

**6.2 Core Red Flags (Original)**

| Red Flag | Research Questions |
|----------|-------------------|
| **Carryover Loss Unused** | How do carryforwards work? How to detect? What's the alert threshold? |
| **Bracket Boundary Alert** | At what proximity to alert? (e.g., within $5K of next bracket) |
| **RSU Underwithholding** | Calculate: 22% withheld vs actual marginal rate. When is gap significant? |
| **ISO AMT Exposure** | How to calculate AMT risk? What exercise amount triggers concern? |
| **401k Not Maxed** | YTD contribution tracking. How to project year-end? |
| **Tax-Loss Harvesting Opportunity** | Minimum loss threshold? Wash sale warning rules? |
| **Estimated Tax Penalty Risk** | Safe harbor rules (100%/110%). When to alert? |
| **SALT Cap Impact** | How to calculate lost deduction value? |
| **Charitable Bunching Opportunity** | When does bunching beat annual giving? |
| **Concentration Risk** | What % of net worth triggers alert? (10%? 20%?) |

---

**6.3 NEW: Investment Sale & Capital Gains Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **Short-Term Sale Warning** | Selling position held < 1 year | Tax difference STCG vs LTCG? At what gain threshold to alert? |
| **Near Long-Term Threshold** | Position held 330-364 days with gain | How to calculate days-to-wait vs stock risk tradeoff? |
| **LTCG 0% Rate Opportunity** | Income low enough for 0% rate | Thresholds by filing status? How to project year-end income? |
| **LTCG Rate Jump (15%→20%)** | Sale pushes income over $533K/$600K | How to split sale across years? |
| **NIIT Threshold Warning** | MAGI approaching $200K/$250K | What counts as NII? How to minimize exposure? |
| **NIIT Triggered by Sale** | Capital gain pushes MAGI over threshold | Calculate incremental 3.8% cost of sale |

**Detection Logic to Research:**
```
holding_period = sale_date - acquisition_date
if holding_period < 365 days AND gain > threshold:
    alert("SHORT_TERM_GAIN_WARNING")
    tax_savings = gain * (ordinary_rate - ltcg_rate)
```

---

**6.4 NEW: Wash Sale Violation Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **Wash Sale Warning** | Sold at loss + bought same within 30 days | What is "substantially identical"? Does mutual fund ≠ ETF? |
| **DRIP Wash Sale Risk** | Dividend reinvestment on position being harvested | How to detect DRIP status from Plaid data? |
| **Cross-Account Wash Sale** | Bought same security in IRA within 30 days | Is IRA wash sale loss permanently disallowed? |
| **Spouse Account Wash Sale** | Spouse holds same security | How to handle spouse data (manual input vs integration)? |
| **RSU Vesting Wash Sale** | RSU vesting within 30 days of loss sale | How common is this? Detection from vest schedule? |

**Detection Logic to Research:**
```
for each sale at loss:
    window = [sale_date - 30 days, sale_date + 30 days]
    for each purchase in window:
        if substantially_identical(sold, purchased):
            alert("WASH_SALE_VIOLATION")
            disallowed_loss = calculate_disallowed()
```

**Key Research Questions:**
- What constitutes "substantially identical" security?
- How does wash sale affect cost basis of replacement shares?
- Wash sale across accounts (taxable → IRA) - is loss permanently lost?

---

**6.5 NEW: Dividend Qualification Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **Dividend Disqualified** | Sold stock <61 days after ex-div date | 61-day holding period calculation? 121-day window? |
| **REIT in Taxable Account** | REIT holdings in taxable brokerage | REIT dividends always ordinary - asset location alert? |
| **High-Yield Tax Inefficiency** | Dividend yield >3% in taxable account | When is moving to tax-advantaged worth it? |

**Key Research Questions:**
- Exact 61-day rule: How is the 121-day window calculated?
- Which dividends are NEVER qualified (REITs, MLPs, money markets)?
- Preferred stock holding period (91 days in 181-day window)?

---

**6.6 NEW: ESPP Disposition Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **Disqualifying Disposition Warning** | Selling before 2yr/1yr holding | Tax difference qualifying vs disqualifying? |
| **Near Qualifying Date** | Within 60 days of qualifying threshold | How to calculate both dates (offering + purchase)? |
| **ESPP Concentration vs Tax** | Large ESPP position, long to qualify | Framework for risk vs tax optimization? |

**Holding Period Requirements:**
- > 2 years from offering (grant) date, AND
- > 1 year from purchase date

**Detection Logic to Research:**
```
days_from_offering = today - offering_date
days_from_purchase = today - purchase_date

if days_from_offering > 730 AND days_from_purchase > 365:
    disposition = "QUALIFYING"
else:
    disposition = "DISQUALIFYING"
    days_to_qualify = max(730 - days_from_offering, 365 - days_from_purchase)
```

---

**6.7 NEW: Expanded Equity Compensation Red Flags**

**RSU Additions:**
| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **Large Vest Bracket Jump** | Vest pushes into higher bracket | Calculate marginal rate change from vest income? |
| **RSU Near 1-Year Holding** | Shares held 330-364 days post-vest | Track per-lot holding periods for LTCG eligibility? |

**ISO Additions:**
| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **$100K ISO Limit Exceeded** | ISOs vesting >$100K FMV/year | How to detect when excess becomes NSO? |
| **ISO Qualifying Sale Near** | Approaching 2yr grant / 1yr exercise | How to track both dates per lot? |
| **Stock Dropped Post-Exercise** | Price < exercise price, AMT paid | "Phantom gain" problem - when to alert? |
| **CA ISO Tax Warning** | CA resident exercising ISOs | CA taxes bargain element regardless of hold - alert? |

---

**6.8 NEW: Life Event Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **Marriage Tax Impact** | Filing status changed to MFJ | Marriage penalty vs bonus calculation? |
| **Divorce Filing Status** | Recently divorced, need W-4 update | When to prompt for W-4 review? |
| **Home Sale Exclusion Limit** | Gain may exceed $250K/$500K | How to estimate home gain from Plaid/manual? |
| **Home Sale 2-Year Rule** | Selling before 2-year ownership | Partial exclusion rules? |
| **Job Change Multi-State** | New job in different state | Multi-state income allocation complexity? |
| **ISO 90-Day Expiration** | Left company, ISOs expiring | Standard 90-day post-termination window? |
| **New Dependent Credits** | Had child, not claiming CTC | CTC phase-out thresholds ($200K/$400K)? |

---

**6.9 NEW: Retirement Account Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **HSA Not Maxed** | Has HDHP but not maxing HSA | How to detect HDHP status? |
| **Catch-Up Eligible Unused** | Age 50+ not using catch-up | Age detection method? |
| **Roth Conversion Opportunity** | Room in current bracket | Calculate bracket ceiling space? |
| **Backdoor Roth Pro-Rata Risk** | Traditional IRA balance + high income | Pro-rata rule calculation? |
| **RMD Deadline Warning** | Age 73+ with required distribution | RMD calculation formula? |

---

**6.10 NEW: Threshold Proximity Alerts**

| Threshold | 2025 Amount (Single/MFJ) | Alert When Within | Impact |
|-----------|-------------------------|-------------------|--------|
| NIIT | $200K / $250K | $25,000 | 3.8% surtax on investment income |
| Additional Medicare | $200K / $250K | $25,000 | 0.9% additional Medicare tax |
| 24% → 32% Bracket | $197,300 / $394,600 | $15,000 | 8% rate jump |
| 32% → 35% Bracket | $250,525 / $501,050 | $15,000 | 3% rate jump |
| LTCG 0% → 15% | $48,350 / $96,700 | $10,000 | 15% on gains |
| LTCG 15% → 20% | $533,400 / $600,050 | $25,000 | 5% rate jump |
| AMT Exemption Phase-out | $626,350 / $1,252,700 | $50,000 | Exemption reduces |
| Roth IRA Eligibility | $165,000 / $246,000 | $20,000 | Cannot contribute directly |

---

**6.11 NEW: Year-End Deadline Red Flags**

| Deadline | Date | Red Flag Trigger |
|----------|------|------------------|
| Tax-Loss Harvesting | Dec 31 | Unrealized losses available, gains to offset |
| Charitable Contributions | Dec 31 | Bunching opportunity identified |
| 401(k) Max | Dec 31 | Not on track to max with remaining paychecks |
| HSA Max (payroll) | Dec 31 | Below limit with December deadline |
| State Estimated Payment | Dec 31 | CA/NY SALT prepay strategy |
| Roth Conversion | Dec 31 | Bracket space available, not converted |
| Q4 Estimated Payment | Jan 15 | Payment due, may be underpaid |
| IRA/HSA Contribution | Apr 15 | Prior year contribution still possible |

---

**6.12 NEW: California-Specific Red Flags**

| Red Flag | Trigger Condition | Research Questions |
|----------|------------------|-------------------|
| **CA No LTCG Preference** | Large capital gain, CA resident | CA taxes LTCG as ordinary (up to 13.3%)? |
| **CA ISO Taxation** | ISO exercise in CA | CA taxes bargain element at exercise? |
| **Mental Health Tax** | CA income >$1M | +1% tax over $1M threshold? |
| **CA Safe Harbor** | Prior year CA income >$1M | Cannot use 100% prior year safe harbor? |

---

**6.13 Red Flag Priority Matrix**

| Priority | Criteria | Examples |
|----------|----------|----------|
| **CRITICAL** | Immediate action required, large $ impact | AMT >$50K, safe harbor violation, wash sale imminent |
| **HIGH** | Action within 30 days, significant savings | Holding period near LTCG, ESPP qualifying soon |
| **MEDIUM** | Address this quarter | 401k not maxed, Roth conversion opportunity |
| **LOW** | Annual review item | Asset location, dividend efficiency |

---

**6.14 Research Alert Best Practices**
Search for:
- Financial app notification UX patterns
- Alert fatigue prevention
- Prioritization frameworks for alerts
- How Mint/Empower/others handle alerts

### Output Format
Create specification document with:
1. **Prioritized list of 50+ red flags** (expanded from original 10)
2. For each red flag:
   - Trigger condition (formula/logic)
   - Required data inputs
   - Alert copy (title + description)
   - Suggested action
   - Priority/severity level
3. Alert display UX recommendations
4. **Detection algorithm pseudocode for complex rules** (wash sale, holding periods)

---

## Red Flag Summary by Category

| Category | # Red Flags | Data Sources |
|----------|-------------|--------------|
| Core (Original) | 10 | Various |
| Capital Gains & Sales | 6 | Holdings, transactions, income |
| Wash Sales | 5 | Transactions (all accounts), RSU vests |
| Dividend Qualification | 3 | Dividend history, holding periods |
| ESPP Dispositions | 3 | Offering/purchase dates |
| Equity Comp (Expanded) | 6 | Grants, exercises, vests |
| Life Events | 7 | Manual input |
| Retirement Accounts | 5 | Balances, contributions |
| Threshold Proximity | 8 | Income projections |
| Year-End Deadlines | 8 | Calendar, account status |
| California-Specific | 4 | State, income |
| **TOTAL** | **65** | |

---
## Research Task 7: What-If Sliders

### Objective
Research and specify the interactive scenario modeling sliders, including calculation formulas and UI patterns.

### Research Instructions

**7.1 Research Existing What-If Tools**
Analyze how these tools implement scenario modeling:
- Range's what-if features
- Holistiplan scenario comparison
- Fidelity retirement planner
- Vanguard Roth conversion calculator
- TurboTax "what if" tools

Document:
- What scenarios do they offer?
- UI patterns (sliders, inputs, visualizations)
- How results are displayed
- Real-time vs. calculate button

**7.2 For Each Slider Category, Research:**

**Retirement Sliders:**
| Slider | Research Questions |
|--------|-------------------|
| 401k Contribution | Current limits, catch-up, employer match impact |
| Roth Conversion | Tax cost calculation, break-even analysis, IRMAA impact |
| HSA Contribution | Limits, triple tax advantage math |
| Backdoor Roth | Pro-rata rule, step transaction doctrine |

**Equity Compensation Sliders:**
| Slider | Research Questions |
|--------|-------------------|
| RSU Sell Timing | Tax difference (ordinary vs LTCG), what assumptions? |
| RSU Sell Amount | Bracket impact, concentration change calculation |
| ISO Exercise | AMT calculation, optimal exercise strategy research |
| ESPP Participation | Return calculation with discount + lookback |

**Income/Deduction Sliders:**
| Slider | Research Questions |
|--------|-------------------|
| Charitable Giving | Tax savings formula, appreciated stock benefit |
| Charitable Bunching | Multi-year comparison math |
| Bonus Timing | Year-to-year bracket comparison |

**Life Event Sliders:**
| Slider | Research Questions |
|--------|-------------------|
| State Move | Tax savings by state comparison |
| Home Purchase | Mortgage interest deduction value, standard deduction comparison |
| Marriage | Marriage penalty/bonus calculation |

**7.3 Research Slider UI/UX**
Search for:
- Best practices for financial calculators
- Real-time calculation patterns
- Slider vs. input field decision criteria
- Mobile-friendly slider implementations
- Accessibility requirements

**7.4 Research Calculation Accuracy**
For each slider, determine:
- Required precision
- Assumptions to disclose
- Edge cases that break the model
- When to show "consult a professional"

### Output Format
Create specification document with:
1. Prioritized list of 15-20 sliders for MVP
2. For each slider:
   - Input parameters (min, max, default, step)
   - Calculation formula
   - Output display (what numbers to show)
   - Assumptions and limitations
   - Required user data
3. UI/UX recommendations
4. Dependency map (which sliders need which data)

---

## Research Task 8: Technical Implementation

### Objective
Research technical approaches, libraries, and architecture for building the tax engine.

### Research Instructions

**8.1 Tax Calculation Libraries**
Search GitHub and package managers for:
- Python tax calculation libraries
- JavaScript tax calculators
- Any language tax engines

Evaluate:
- Accuracy
- Maintenance status
- Coverage (federal, state, AMT)
- Extensibility

**8.2 Architecture Patterns**
Research how to structure:
- Tax calculation engine
- Real-time slider calculations
- Alert/red flag detection
- Multi-year projections

Search for:
- Financial calculation engine architectures
- Event-driven tax tracking
- Rule engines for alerts

**8.3 Testing & Validation**
Research:
- How to validate tax calculations
- IRS test scenarios
- Comparison testing against TurboTax
- Edge case identification

**8.4 Annual Update Process**
Research:
- When IRS releases new year brackets
- How tax software handles law changes
- Data sources for tax law updates

### Output Format
Create technical specification with:
1. Recommended libraries and tools
2. Architecture diagram
3. Data model schema
4. Testing strategy
5. Update/maintenance plan

---

## Research Task 9: User Trust & Data Sensitivity (NEW)

### Objective
Research user psychology around trusting new financial apps with sensitive personal data, and identify strategies to overcome trust barriers for TaxLens adoption.

### The Core Problem
TaxLens requires users to share extremely sensitive information:
- Income details (W-2, bonuses, equity compensation)
- Investment holdings and transactions
- Tax returns / prior year data
- Social Security numbers (potentially)
- Bank account connections (via Plaid)
- Employment details

**Key Question:** Why would a user trust a NEW app with this data when established players (TurboTax, Mint, Empower) already exist?

### Research Instructions

**9.1 User Trust Psychology for Financial Apps**

Search for:
- "Why users trust financial apps" research studies
- "Fintech adoption barriers" academic papers
- "Personal finance app trust factors" surveys
- User research on Mint, Empower, Robinhood adoption
- "Privacy concerns financial apps" studies

**Research Questions:**
| Question | Why It Matters |
|----------|----------------|
| What makes users trust a new financial app? | Core adoption driver |
| What's the #1 barrier to sharing financial data? | What to address first |
| How long before users trust an app with sensitive data? | Onboarding timeline |
| Do users trust startups vs established brands differently? | Positioning strategy |
| What security signals do users look for? | UI/messaging priorities |

**9.2 Sensitive Data Hierarchy**

Research what data users are most/least willing to share:

| Data Type | Sensitivity Level | Research Questions |
|-----------|------------------|-------------------|
| Email address | Low | Baseline - everyone asks |
| Income range | Medium | How specific before discomfort? |
| Exact salary | High | When do users share this? |
| Investment holdings | High | Read-only vs transaction access? |
| Bank account (Plaid) | Very High | What % of users connect? Drop-off rate? |
| Tax returns | Very High | When is this appropriate to ask? |
| SSN | Extreme | Do tax apps need this? When? |

**Search for:**
- "Plaid connection drop-off rate" 
- "Bank linking abandonment fintech"
- "User willingness to share income data"
- Surveys on financial data sharing comfort levels

**9.3 Trust-Building Strategies**

Research how successful fintech apps build trust:

**Security Signals:**
| Signal | Research Questions |
|--------|-------------------|
| SOC 2 Certification | Do users know/care? Does it increase conversion? |
| Bank-level encryption | Effective messaging? |
| "Read-only access" | Does this reduce friction for Plaid? |
| Two-factor authentication | Expected or differentiator? |
| Privacy policy | Do users read it? What matters? |
| Data deletion options | Important for trust? |

**Social Proof:**
| Signal | Research Questions |
|--------|-------------------|
| User count ("1M users trust us") | Threshold for credibility? |
| Company backing (YC, a]6z, etc.) | Does VC credibility transfer? |
| Press coverage | Which outlets matter? |
| App store ratings | Minimum rating for trust? |
| Testimonials | Effective or ignored? |
| "As seen in Forbes/WSJ" | Impact on trust? |

**Brand & Design:**
| Factor | Research Questions |
|--------|-------------------|
| Professional design | Does polish = trust? |
| Founder story / team page | Does transparency help? |
| Physical address | Do users check? |
| Customer support access | Chat vs email vs phone? |

**9.4 Competitor Trust Strategies**

Analyze how competitors build trust:

| Competitor | Trust Strategy | Research Questions |
|------------|----------------|-------------------|
| **TurboTax** | 40-year brand, IRS partnership, guarantees | What can a startup replicate? |
| **Mint** | Intuit acquisition, 20M users | How did they start from zero? |
| **Empower** | "Bank-level security" messaging | Effective positioning? |
| **Robinhood** | VC backing, viral growth | Trust despite controversies? |
| **Plaid** | Powers major apps, bank partnerships | How do they communicate security? |
| **Range** | Premium positioning, advisor access | Does high price = trust? |

**Search for:**
- How Mint got first 1M users (trust strategy)
- Robinhood security messaging
- Plaid trust communication
- How fintech startups overcome trust barriers
- Case studies: fintech app launches

**9.5 Progressive Data Collection**

Research strategies for gradual trust-building:

| Stage | Data Requested | Value Provided | Research Questions |
|-------|---------------|----------------|-------------------|
| **Stage 1** | Email only | Basic tax tips, newsletter | Conversion rate? |
| **Stage 2** | Income range, state, filing status | Rough tax estimate | % who continue? |
| **Stage 3** | Detailed income, deductions | Accurate projection | Drop-off rate? |
| **Stage 4** | Plaid connection | Full automation, red flags | % who connect? |
| **Stage 5** | Tax documents | Complete analysis | When is this appropriate? |

**Research Questions:**
- What's the optimal progressive disclosure flow?
- How much value must be shown before asking for sensitive data?
- Can you provide useful tax intelligence WITHOUT Plaid?
- What's the "aha moment" that builds trust?

**9.6 Privacy & Compliance Requirements**

Research regulatory requirements that also build trust:

| Regulation | Requirements | Trust Signal |
|------------|--------------|--------------|
| **CCPA** (California) | Disclosure, deletion rights | "California Privacy Rights" badge |
| **GDPR** (if applicable) | Consent, portability | EU compliance messaging |
| **SOC 2 Type II** | Security audit | Certification badge |
| **PCI DSS** (if payments) | Card data security | Not directly applicable? |
| **IRS e-file** (if filing) | Authorization | "IRS Authorized" badge |

**Search for:**
- Fintech compliance requirements
- Privacy certifications that matter to users
- Security audit costs for startups
- Trust badges that increase conversion

**9.7 Failure Modes & Data Breaches**

Research what destroys trust:

| Risk | Impact | Mitigation Research |
|------|--------|---------------------|
| Data breach | Company-ending | Breach notification best practices |
| Plaid outage | Temporary frustration | Fallback strategies |
| Calculation error | Loss of credibility | Error handling, disclaimers |
| Selling data | Reputation destruction | Privacy policy clarity |
| Shutdown/acquisition | Data fate concerns | Data portability promises |

**Search for:**
- Fintech data breach case studies
- How companies recover from breaches
- "What happens to my data if you shut down"
- User concerns about data selling

**9.8 Target User Trust Profile**

Research trust characteristics of TaxLens target users:

**High-income tech professionals ($200K-$1M):**
- More or less trusting of new apps than average?
- Tech-savvy = more security aware?
- Time-constrained = willing to trade privacy for convenience?
- Already using Plaid-connected apps?

**Search for:**
- "High income user fintech adoption"
- "Tech professional financial app preferences"  
- Demographics of Mint/Empower/Robinhood users
- Trust factors by income level

### Output Format

Create specification document with:

1. **Trust Barrier Analysis**
   - Ranked list of user concerns
   - Data sensitivity hierarchy
   - Drop-off points in onboarding

2. **Trust-Building Playbook**
   - Required security certifications
   - Messaging and positioning
   - Social proof strategy
   - Progressive disclosure flow

3. **MVP Trust Requirements**
   - Minimum security features for launch
   - Required compliance items
   - Trust messaging copy
   - "Day 1" vs "Later" trust features

4. **Competitor Trust Teardown**
   - Screenshots of trust messaging
   - Security pages analysis
   - Onboarding flow comparison

5. **Risk Mitigation Plan**
   - Data breach response plan
   - Error handling strategy
   - Shutdown/portability promises

---

## Execution Instructions for AI

### How to Execute This Research Plan

For each Research Task:

1. **Search comprehensively** - Use web search for multiple queries per topic
2. **Document sources** - Include URLs for all findings
3. **Synthesize findings** - Don't just list; analyze and recommend
4. **Flag uncertainties** - Note where information is unclear or conflicting
5. **Create structured output** - Follow the Output Format specified

### Priority Order

Execute in this order (dependencies):
1. **Task 1 (Existing Solutions)** - First! Don't reinvent the wheel
2. **Task 2 (Federal Tax)** - Foundation for everything
3. **Task 3 (Equity Comp)** - Key differentiator
4. **Task 6 (Red Flags)** - Can start parallel to 2-3
5. **Task 7 (Sliders)** - Can start parallel to 2-3
6. **Task 9 (User Trust)** - Critical for product decisions, start early
7. **Task 4 (State Tax)** - After federal is solid
8. **Task 5 (Data Mapping)** - After tax rules are understood
9. **Task 8 (Technical)** - After requirements are clear

### Output Consolidation

After all tasks complete, create:
1. **Master specification document** - All findings combined
2. **Implementation roadmap** - Prioritized build order
3. **Risk register** - Technical and accuracy risks identified
4. **Open questions** - Items needing human decision

---

## Success Criteria

### Research is complete when:
- [ ] All 9 tasks have documented outputs
- [ ] AI/LLM options evaluated with recommendation (build vs. use existing)
- [ ] Existing solutions are catalogued with recommendations
- [ ] Tax calculations have formulas and test cases
- [ ] **65+ red flags have trigger logic and copy** (expanded from 10)
- [ ] **Investment sale timing alerts specified**
- [ ] **Wash sale detection algorithm designed**
- [ ] **ESPP disposition tracking defined**
- [ ] **Life event tax impacts documented**
- [ ] **Threshold proximity alerts configured**
- [ ] Sliders have calculation formulas and input specs
- [ ] Technical approach is recommended (including AI strategy)
- [ ] **User trust barriers identified and ranked**
- [ ] **Progressive data collection flow designed**
- [ ] **Minimum trust/security requirements for MVP defined**
- [ ] Gaps and risks are identified

---

*Research Plan v3.1 - Expanded Red Flags + User Trust*
*Created: January 2026*
*v3 Updates: Task 6 expanded from 10 to 65+ red flags*
*v3.1 Updates: Added Task 9 (User Trust & Data Sensitivity) addressing adoption barriers for new financial apps*
