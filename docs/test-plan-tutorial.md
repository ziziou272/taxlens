# Test Plan — User Tutorial Redesign

## Scope
All UI changes from the user tutorial redesign (P0–P2). Covers onboarding, navigation, Tax Tips, What If, Dashboard, Tax Input Form, and Glossary.

---

## 1. Onboarding Flow

### 1.1 First Launch
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 1 | Value pages shown | Fresh install → open app | Page 1: "See your taxes clearly" with 3 features |
| 2 | Page navigation | Tap "Next" | Advances through all 5 pages in order |
| 3 | Back button | On page 3, tap "Back" | Returns to page 2 |
| 4 | Back hidden on page 1 | On page 1 | No back button visible |
| 5 | Page dots | Navigate pages | Active dot is wider (24px), brand color; inactive dots are 8px |
| 6 | Filing status selection | Page 3 | All 4 options shown with descriptions; tap to select |
| 7 | State selection | Page 4 | 5 states shown with tax info; "No income tax ✨" for WA/TX/FL |
| 8 | Income range hints | Page 5, select "$250k-$500k" | Shows "💡 AMT may apply to you" |
| 9 | Finish onboarding | Select all options, tap "Get Started" | Navigates to Dashboard; onboarding not shown again |

### 1.2 Returning User
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 10 | Skip onboarding | Relaunch after completing onboarding | Goes directly to Dashboard |
| 11 | Reset onboarding | Settings → "Reset Onboarding" → restart | Onboarding shown again |

---

## 2. Navigation

| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 12 | Tab labels | View bottom nav | "Dashboard", "Tax Tips", "What If", "Settings" |
| 13 | Tab icons | View bottom nav | Dashboard, Lightbulb, Explore, Settings icons |
| 14 | Tab navigation | Tap each tab | Correct screen loads |

---

## 3. Tax Tips (formerly Alerts)

### 3.1 Empty State
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 15 | Empty state content | Navigate to Tax Tips with no calculation done | Shows lightbulb icon, "Personalized tax tips" title, 3 example tips, CTA button |
| 16 | CTA navigates | Tap "Enter your income to get tips" | Navigates to Dashboard |

### 3.2 With Alerts
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 17 | Alert cards display | Calculate taxes → go to Tax Tips | Alert cards shown with priority colors (red/orange/blue) |
| 18 | App bar title | Open Tax Tips | Title reads "Tax Tips" |

---

## 4. What If (formerly Scenarios)

### 4.1 Scenario Picker
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 19 | Question cards | Open What If tab | Cards with questions: "What if I moved?", "What if I sold stocks?", etc. |
| 20 | Card descriptions | View cards | Each has icon, question title, and plain-English description |
| 21 | Card tap | Tap "What if I moved?" | Navigates to detail page with back arrow |
| 22 | Back to picker | Tap back arrow on detail | Returns to card list |

### 4.2 Scenario Detail
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 23 | State move | Select "What if I moved?" | Shows state dropdown + income slider |
| 24 | Run comparison | Adjust params, tap "See the difference" | Shows results with "Now" vs "After change" |
| 25 | Savings display | Result with savings | Green "You'd save" with amount and "X% less tax" |
| 26 | Extra tax display | Result with higher tax | Red "You'd pay more" with amount and "X% more tax" |
| 27 | Breakdown toggle | Tap "Detailed breakdown" | Expands table with human-readable row labels |
| 28 | Breakdown labels | View breakdown | "Federal", "State", "Investment gains", "Social Security & Medicare", "Alt. minimum tax", "Investment surtax" |

---

## 5. Dashboard

### 5.1 Tax Summary Card
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 29 | Title | View dashboard with result | "Your estimated tax this year" |
| 30 | Rate labels | View rate chips | "Avg rate" and "Top rate" (not "Effective" / "Marginal") |
| 31 | Tooltip — avg rate | Tap ℹ️ next to "Avg rate" | Tooltip: "Your total tax divided by total income..." |
| 32 | Tooltip — top rate | Tap ℹ️ next to "Top rate" | Tooltip: "The tax rate on your next dollar..." |
| 33 | Tooltip duration | Trigger tooltip | Stays visible for 5 seconds |

### 5.2 Withholding Bar
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 34 | Title | View bar | "Tax paid so far vs. what you'll owe" |
| 35 | Owe label | Withheld < projected | "You'll owe: $X" in red |
| 36 | Refund label | Withheld > projected | "Refund coming: $X" in green |
| 37 | Paid label | View left side | "Paid: $X" in green |

### 5.3 Empty State
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 38 | No result | Dashboard with no calculation | "Enter your income to see your tax picture" |

---

## 6. Tax Input Form

### 6.1 Basic Mode
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 39 | Default fields | Open form (new user) | Filing status, state, salary, fed withheld, state withheld |
| 40 | Helper text | View salary field | "Your annual pay before taxes (from your W-2 or offer letter)" |
| 41 | State options | View state dropdown | States include tax context ("Washington — no income tax") |
| 42 | Detailed toggle hidden | Default view | Shows "I have stock income, investments, or other income" link |

### 6.2 Detailed Mode
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 43 | Expand | Tap "I have stock income..." | RSU, short-term gains, long-term gains fields appear |
| 44 | Collapse | Tap "Hide additional income" | Advanced fields hidden |
| 45 | Auto-expand | User has RSU income > 0, open form | Detailed mode shown by default |
| 46 | Glossary button | Tap ℹ️ on RSU field | Bottom sheet: "Stock award income" title, "RSU Income" subtitle, explanation |
| 47 | Glossary content | Check all ℹ️ buttons | Each shows friendly name + technical term + multi-sentence explanation |

### 6.3 Calculation
| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 48 | Basic mode calc | Fill salary + withheld, tap "Calculate my tax" | Dashboard updates, form closes |
| 49 | Detailed mode calc | Fill all fields, tap "Calculate my tax" | All values saved including RSU/gains |
| 50 | Loading state | Tap calculate | Button shows spinner + "Calculating..." |

---

## 7. Glossary System

| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 51 | GlossaryTerm widget | Render `GlossaryTerm(term: 'AMT', ...)` | Shows term text + ℹ️ icon |
| 52 | Bottom sheet | Tap GlossaryTerm | Bottom sheet with handle bar, friendly name, technical name (italic), explanation |
| 53 | All 14 entries | Access TaxGlossary.entries | All entries have non-empty term, friendly, and explanation |
| 54 | Long explanation | View any glossary bottom sheet | Text has 1.5 line height, wraps properly |

---

## 8. Regression

| # | Test Case | Steps | Expected |
|---|-----------|-------|----------|
| 55 | Settings unchanged | Open Settings tab | All existing settings work (API URL, reset onboarding, sign in/out) |
| 56 | Auth flow | Login → protected routes | Alerts/Scenarios still require auth when Supabase configured |
| 57 | Dark theme | All screens | Brand color (teal), proper contrast on dark backgrounds |
| 58 | State persistence | Fill form → restart app | Values preserved via SharedPreferences |
| 59 | Supabase sync | Login → change settings → logout → login | Settings restored from Supabase |

---

## Test Environment

- **Device targets:** iPhone 15 Pro (iOS 18), Pixel 8 (Android 15), iPad Air (landscape)
- **Flutter version:** Latest stable (3.x)
- **API backend:** Local (`http://localhost:8100`) or production
- **Auth:** Test with and without Supabase configured

## Automation Notes

- Onboarding page navigation → Widget test with `PageController` verification
- Glossary data completeness → Unit test asserting all entries have required fields
- Tab renaming → Widget test checking `NavigationDestination` labels
- Form basic/detailed toggle → Widget test with `find.byType` assertions
