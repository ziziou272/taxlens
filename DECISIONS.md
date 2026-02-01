# Architecture Decision Records

## ADR-001: Planning Tool First, Filing Later

**Date:** 2026-02-01  
**Status:** Accepted

### Context

We need to decide whether TaxLens should:
1. Be a full tax filing replacement (compete with TurboTax)
2. Be a planning/analysis tool that complements existing filing software

### Decision

**Build a planning tool first.** Filing can be added in v2+ after the calculation engine is battle-tested.

### Rationale

| Filing Tool | Planning Tool |
|-------------|---------------|
| ❌ IRS e-file certification required | ✅ No certification needed |
| ❌ Liability for filing errors | ✅ Projections, no liability |
| ❌ Must support all edge cases | ✅ Can focus on target persona |
| ❌ High stakes, slow iteration | ✅ Low stakes, fast iteration |
| ❌ Competing with $3B TurboTax | ✅ Underserved market gap |

### Consequences

- Users must still file with TurboTax/CPA (slightly annoying)
- We can ship faster and safer
- Calculation engine gets real-world validation before filing

---

## ADR-002: Deterministic Engine, AI for Explanations

**Date:** 2026-02-01  
**Status:** Accepted

### Context

Should we use AI (LLMs) for tax calculations, or build a deterministic rules engine?

### Decision

**100% deterministic calculations.** AI only for explanations, Q&A, and strategy suggestions.

### Rationale

From TurboTax/Intuit's own approach:
> "What generative AI doesn't do well yet is math. So Intuit is not using the AI for calculations, in part to avoid those hallucinations."

LLMs are:
- Probabilistic (can make arithmetic errors)
- Non-reproducible (same input → different output)
- Not auditable (can't explain *why* a calculation happened)

Tax calculations need:
- Exact arithmetic (use Python Decimal, not float)
- Reproducible results
- Auditability for IRS

### Consequences

- More upfront work to encode all tax rules
- But: guaranteed accuracy and auditability
- AI layer is optional/supplementary, not critical path

---

## ADR-003: Python for Calculation Engine

**Date:** 2026-02-01  
**Status:** Accepted

### Context

What language for the core tax calculation engine?

### Decision

**Python with Decimal library.**

### Rationale

1. **PSLmodels/Tax-Calculator** is Python - can leverage existing work
2. **Decimal** module for exact arithmetic (no floating point errors)
3. **NumPy/Pandas** for data manipulation if needed
4. **FastAPI** for clean API layer
5. Easy to test with pytest

### Consequences

- Need Python runtime on server
- Can't run in browser (but can expose via API)
- Great library ecosystem for financial math

---

## ADR-004: Next.js for Frontend

**Date:** 2026-02-01  
**Status:** Accepted

### Context

What frontend framework?

### Decision

**Next.js 14+ with App Router + Tailwind CSS**

### Rationale

1. React ecosystem is familiar and well-documented
2. Server components for data fetching
3. Tailwind for rapid UI development
4. Vercel deployment is trivial
5. TypeScript for type safety

### Consequences

- Modern React patterns required
- Good for SEO if we want content marketing
- Large community for support

---

## ADR-005: Target Persona: High-Income Tech with Equity

**Date:** 2026-02-01  
**Status:** Accepted

### Context

Who is TaxLens for?

### Decision

**Tech employees earning $200K-$1M+ with equity compensation in CA/NY/WA.**

### Rationale

1. **We are the target user** - understand the pain deeply
2. **High willingness to pay** - $99-299/year is nothing vs tax savings
3. **Complex needs** - generic tools don't serve them well
4. **Underserved** - CPAs expensive, TurboTax too basic
5. **Network effects** - tech people know tech people

### Out of Scope (for now)

- Small business / 1099 (different complexity)
- Low-income (different needs, Vita exists)
- Real estate investors (whole other domain)
- Day traders (too complex, too niche)

### Consequences

- Focused feature set
- Can charge premium pricing
- Marketing is targeted

---

## ADR-006: Start with CA, Add NY/WA

**Date:** 2026-02-01  
**Status:** Accepted

### Context

Which states to support first?

### Decision

**California first, then New York, then Washington.**

### Rationale

| State | Tech Workers | Tax Complexity | Priority |
|-------|--------------|----------------|----------|
| CA | Highest concentration | Very high (9.3%-13.3%, AMT) | 1st |
| NY | Major hub | High (4%-10.9% + NYC) | 2nd |
| WA | No income tax BUT... | 7% capital gains over $270K | 3rd |

### Consequences

- Can ship faster with single-state focus
- Add states incrementally based on demand
- Multi-state sourcing is Phase 2+ feature

---

## ADR-007: Privacy-First Data Architecture

**Date:** 2026-02-01  
**Status:** Accepted

### Context

How to handle sensitive financial data?

### Decision

**Encryption at rest + user-controlled data + no selling.**

### Details

1. All PII/financial data encrypted with AES-256
2. User can export all data (GDPR-style)
3. User can delete all data
4. No selling data to third parties
5. Minimal data collection (only what's needed)

### Future

- SOC 2 Type II certification for enterprise
- Option for local-only mode (data never leaves device)

### Consequences

- Trust is critical for adoption
- Some analytics limitations (worth it)
- Higher hosting costs for encryption/security
