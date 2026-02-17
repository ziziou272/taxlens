# TaxLens User Tutorial Design

## Problem Statement

Users opening TaxLens for the first time face three barriers:
1. **No value explanation** — The app immediately asks for tax information without explaining what it does
2. **Jargon overload** — Terms like "Effective Rate", "RSU Income", "AMT", "NIIT" are meaningless to most users
3. **No guidance** — Features like Alerts and Scenarios have no explanation of their purpose

## Design Principles

- **Plain language first** — Every tax term has a human-readable equivalent
- **Progressive disclosure** — Show simple by default, reveal complexity on demand
- **Context over manuals** — Explain things where they appear, not in a separate help page
- **Question-driven** — Frame features as answers to user questions ("What if I moved?")

## Changes Implemented

### 1. Onboarding Redesign (P0)

**Before:** 3 pages of form fields (Filing Status → State → Income Range)

**After:** 5 pages (2 value intro + 3 form pages with context)

| Page | Content |
|------|---------|
| 1 | Value proposition: "See your taxes clearly" + 3 core features |
| 2 | How it works: 3-step flow explanation |
| 3 | Filing status with descriptions ("Not married, no dependents") |
| 4 | State with tax context ("No state income tax ✨") |
| 5 | Income range with relevant tips ("AMT may apply to you") |

### 2. Navigation Renaming (P0)

| Before | After | Icon Change |
|--------|-------|-------------|
| Alerts | Tax Tips | ⚠️ → 💡 |
| Scenarios | What If | ↔️ → 🧭 |

### 3. Tax Tips Empty State (P1)

**Before:** "No alerts. Calculate your taxes first."

**After:** Explains the feature, shows example tips, and provides a CTA to enter income.

### 4. What If Scenario Picker (P0)

**Before:** Technical list of scenario type IDs (rsu_timing, iso_exercise, etc.)

**After:** Question-based cards:
- "What if I moved?" — See state tax comparison
- "What if I sold stocks?" — Calculate capital gains tax
- "What if I got my bonus next year?" — Bracket optimization
- etc.

Each card has a one-sentence plain-language description.

### 5. Dashboard Tooltips (P1)

- "Effective Rate" → "Avg rate" + tap-to-explain tooltip
- "Marginal Rate" → "Top rate" + tap-to-explain tooltip
- "Withholding vs Projected" → "Tax paid so far vs. what you'll owe"
- "Withheld" → "Paid", "Owe" → "You'll owe", "Refund" → "Refund coming"

### 6. Tax Input Form Simplification (P2)

**Before:** 8 fields shown at once (Filing Status, State, W-2 Wages, RSU Income, ST Gains, LT Gains, Fed Withheld, State Withheld)

**After:** Two modes:
- **Basic (default):** Filing status, state, salary, federal withheld, state withheld
- **Detailed (expandable):** RSU income, short-term gains, long-term gains — each with ℹ️ glossary buttons

Auto-expands to detailed if user already has advanced fields filled.

### 7. Glossary System (P2)

New reusable `GlossaryTerm` widget and `TaxGlossary` data class covering 14 tax terms:

| Term | Friendly Name | 
|------|--------------|
| Effective Tax Rate | Average tax rate |
| Marginal Tax Rate | Top tax rate |
| W-2 Wages | Salary / paycheck income |
| RSU Income | Stock award income |
| Short-Term Capital Gains | Quick investment profits |
| Long-Term Capital Gains | Investment profits (1+ year) |
| Tax Withholding | Tax already paid from paychecks |
| Filing Status | How you file |
| AGI | Your income after adjustments |
| Standard Deduction | Free tax-exempt amount |
| AMT | Alternative minimum tax |
| NIIT | Investment surtax |
| FICA | Social Security & Medicare tax |
| ISO | Employee stock options |

Each entry includes a multi-sentence plain-language explanation shown in a bottom sheet.

## File Changes

| File | Change |
|------|--------|
| `features/onboarding/onboarding_screen.dart` | Complete rewrite — 5-page flow |
| `features/alerts/alerts_screen.dart` | Rename + new empty state |
| `features/scenarios/scenarios_screen.dart` | Rename + question-based picker + friendly labels |
| `features/dashboard/widgets/tax_summary_card.dart` | Friendly labels + tooltips |
| `features/dashboard/widgets/tax_input_form.dart` | Basic/detailed modes + glossary |
| `features/dashboard/widgets/withholding_gap_bar.dart` | Friendly labels |
| `features/dashboard/dashboard_screen.dart` | Minor label update |
| `core/widgets/glossary_tooltip.dart` | **New** — reusable glossary system |
| `router.dart` | Tab names + icons |

## Future Work

- [ ] Localization (Chinese + English) for all friendly terms
- [ ] Analytics: track which glossary terms users tap most
- [ ] A/B test onboarding completion rates
- [ ] Add more states to the onboarding state picker
- [ ] Contextual tutorial overlays (coach marks) for first-time dashboard view
