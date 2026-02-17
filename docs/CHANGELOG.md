# Changelog

## [Unreleased] - 2026-02-17

### Added
- **Onboarding value pages** — Two new intro screens explaining what TaxLens does and how it works, shown before the setup form
- **Glossary system** — New `GlossaryTerm` widget and `TaxGlossary` data class with 14 plain-language tax term explanations (tap ℹ️ to learn)
- **Tax Input basic/detailed modes** — Income form defaults to 3 essential fields; stock/investment fields hidden behind "I have stock income..." toggle
- **Tax Tips empty state** — When no alerts exist, shows feature explanation with example tips and CTA to enter income
- **Contextual hints** in onboarding — Filing status options now include descriptions; states show tax rate info; income ranges show relevant tips

### Changed
- **Alerts tab → Tax Tips** — Renamed with lightbulb icon (was warning icon)
- **Scenarios tab → What If** — Renamed with explore icon (was compare-arrows icon)
- **Scenario picker** — Replaced technical type-ID list with question-based cards ("What if I moved?", "What if I sold stocks?", etc.)
- **Dashboard labels** — "Effective Rate" → "Avg rate", "Marginal Rate" → "Top rate" with tap-to-explain tooltips
- **Withholding bar** — "Withholding vs Projected" → "Tax paid so far vs. what you'll owe"; "Withheld" → "Paid"; "Owe" → "You'll owe"; "Refund" → "Refund coming"
- **Scenario results** — "Current/Alternative" → "Now/After change"; "Tax Breakdown" → "Detailed breakdown"; breakdown row labels humanized (FICA → "Social Security & Medicare", NIIT → "Investment surtax", LTCG Tax → "Investment gains")
- **Onboarding form pages** — Radio buttons replaced with descriptive card-style selectors
- **Tax Input form** — All fields now have helper text explaining where to find the number

### Technical
- New file: `lib/core/widgets/glossary_tooltip.dart`
- Flutter analyze: 0 errors, 0 warnings (1 suppressed unused_element)
