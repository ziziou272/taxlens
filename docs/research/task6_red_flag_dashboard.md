# Task 6: Red Flag Dashboard (65+ Alerts) - Research Findings

**Research Date:** January 2026
**Version:** 1.0

---

## Executive Summary

This document specifies 65+ tax planning alerts for the TaxLens Red Flag Dashboard. Alerts are categorized by priority (Critical, Warning, Info) and tax domain. Key alert categories:

1. **Underwithholding Alerts** (12 alerts) - Prevent April surprises
2. **AMT Alerts** (10 alerts) - ISO exercise planning
3. **Capital Gains Alerts** (11 alerts) - Threshold monitoring, wash sales
4. **Equity Compensation Alerts** (14 alerts) - RSU, ISO, ESPP optimization
5. **State Tax Alerts** (8 alerts) - Multi-state sourcing, WA cap gains
6. **Retirement & Savings Alerts** (6 alerts) - 401(k), HSA optimization
7. **Year-End Planning Alerts** (7 alerts) - Deadline reminders

---

## Alert Priority Levels

| Priority | Color | Action Required | Example |
|----------|-------|-----------------|---------|
| **CRITICAL** | Red | Immediate action needed | $20K+ underwithholding |
| **WARNING** | Orange | Review within 30 days | AMT exposure on ISO exercise |
| **INFO** | Blue | Awareness/optimization | Tax-loss harvesting opportunity |

---

## 1. Underwithholding Alerts (12)

### 1.1 Critical Underwithholding Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| UW-001 | **Critical Underwithholding** | (Estimated Tax - Total Withheld) > $20,000 | "You're projected to owe **${gap}** at tax time. Consider making an estimated payment or increasing W-4 withholding before {deadline}." |
| UW-002 | **Safe Harbor Violation Risk** | (YTD Withheld < 90% of Current Year Tax) AND (YTD Withheld < 110% of Prior Year Tax) | "You may face underpayment penalties. You've paid ${withheld} but owe ${estimated}. Safe harbor requires ${required}." |
| UW-003 | **Q4 Withholding Emergency** | (Q4 start) AND (Remaining Gap > $15,000) AND (Days until Dec 31 < 60) | "Only {days} days left to cover ${gap} underwithholding. Request additional withholding from your employer immediately." |

### 1.2 Warning Underwithholding Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| UW-004 | **RSU Underwithholding** | (RSU Income × Marginal Rate) > (RSU Income × 0.22) + $5,000 | "Your RSUs are only withheld at 22%, but your marginal rate is {rate}%. You're ${gap} short on {rsu_income} in RSU income." |
| UW-005 | **Bonus Underwithholding** | (Bonus × Marginal Rate) > (Bonus × 0.22) + $3,000 | "Your ${bonus} bonus was withheld at 22%. At your {rate}% rate, you're ${gap} underwitheld." |
| UW-006 | **Million Dollar Threshold** | Supplemental Income approaches $1M | "Approaching $1M supplemental income threshold. Withholding rate increases from 22% to 37% on next ${amount}." |
| UW-007 | **State Underwithholding (CA)** | CA Resident AND (CA Tax - CA Withheld) > $5,000 | "California state tax underwithholding of ${gap}. CA taxes income at up to 13.3%." |
| UW-008 | **State Underwithholding (NY)** | NY Resident AND (NY Tax - NY Withheld) > $5,000 | "New York state tax underwithholding of ${gap}. Consider NYC tax if resident." |

### 1.3 Info Underwithholding Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| UW-009 | **Estimated Payment Reminder** | Days until estimated payment due < 14 | "Q{quarter} estimated taxes due {date}. Consider ${suggested} payment to stay on track." |
| UW-010 | **Year-End True-Up** | December AND (Gap > $5,000) | "Request extra withholding from your final paycheck to avoid April surprise." |
| UW-011 | **FICA Underwithholding** | Employer hasn't withheld proper Social Security | "Verify FICA withholding on W-2. Social Security wage base is ${wage_base}." |
| UW-012 | **Self-Employment Tax** | Side income > $400 | "Your ${side_income} side income triggers self-employment tax of ~${se_tax}. Factor into estimates." |

---

## 2. AMT Alerts (10)

### 2.1 Critical AMT Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| AMT-001 | **Large ISO Exercise AMT Exposure** | ISO Bargain Element > $100,000 | "Exercising these ISOs adds ${bargain} to AMT income. Estimated AMT: ${amt_estimate}. Consider spreading across years." |
| AMT-002 | **Phantom Income - No Cash for Tax** | ISO Exercise with (AMT Due > Liquid Cash × 0.5) | "You may owe ${amt_due} in AMT but haven't sold stock. Ensure cash available or consider same-day sale." |
| AMT-003 | **AMT Exemption Phase-Out** | AMTI > Phase-out Threshold | "Your AMT income of ${amti} triggers exemption phase-out. AMT exemption reduced by ${reduction}." |

### 2.2 Warning AMT Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| AMT-004 | **ISO Exercise Planning** | ISO Available AND Current Year AMT Exposure Low | "Good year to exercise ISOs. Current AMT exposure is low. Consider exercising up to ${optimal} to stay under AMT." |
| AMT-005 | **AMT Credit Carryforward** | Prior Year AMT Paid > 0 | "You have ${amt_credit} AMT credit to recover. May be usable this year if regular tax exceeds AMT." |
| AMT-006 | **OBBBA AMT Change Warning** | Tax Year = 2026 | "Starting 2026, AMT exemption phases out faster. Plan ISO exercises accordingly." |
| AMT-007 | **Multi-Year ISO Spread** | Large ISO Grant AND Years to Expiration > 2 | "Spread ${total_shares} ISO exercises over {years} years to minimize AMT in any single year." |

### 2.3 Info AMT Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| AMT-008 | **AMT Preference Items** | Has ISOs OR Large State Tax Deduction | "Monitor AMT preference items: ISO spread, state tax deduction (limited under AMT)." |
| AMT-009 | **ISO $100K Rule** | Exercisable ISOs > $100K FMV in Year | "More than $100K of ISOs exercisable this year. Excess treated as NSOs." |
| AMT-010 | **Disqualifying Disposition Option** | ISO Exercised AND Stock Down | "Stock dropped since ISO exercise. Disqualifying sale before year-end eliminates AMT on this spread." |

---

## 3. Capital Gains Alerts (11)

### 3.1 Critical Capital Gains Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| CG-001 | **WA Capital Gains Threshold** | WA Resident AND LTCG > $250,000 | "You've exceeded WA capital gains threshold. ${excess} subject to 7-9.9% WA tax (${wa_tax})." |
| CG-002 | **Wash Sale Violation** | Sale at Loss AND Repurchase within 30 days | "Wash sale detected: ${security} sold at loss, repurchased within 30 days. ${loss} loss disallowed." |
| CG-003 | **NIIT Threshold Exceeded** | AGI > $200K (single) / $250K (MFJ) AND Investment Income > $10K | "Net Investment Income Tax (3.8%) applies. Investment income of ${investment_income} over threshold." |

### 3.2 Warning Capital Gains Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| CG-004 | **Tax-Loss Harvesting Opportunity** | Holding with Unrealized Loss > 10% | "${security} is down ${percent}% (${loss}). Consider harvesting loss to offset gains." |
| CG-005 | **Short-Term to Long-Term Transition** | Holding approaching 1-year anniversary | "${security} becomes long-term in {days} days. Holding saves ${savings} in taxes." |
| CG-006 | **Capital Loss Carryforward** | Prior Year Capital Loss Carryforward > 0 | "You have ${carryforward} in capital loss carryforward. Use to offset gains this year." |
| CG-007 | **Concentrated Position Risk** | Single holding > 40% of portfolio | "${security} is {percent}% of your portfolio. Consider diversifying ${amount} for risk management." |
| CG-008 | **LTCG Rate Bracket Change** | Approaching 15% to 20% bracket | "Additional ${amount} in gains pushes you into 20% LTCG bracket." |

### 3.3 Info Capital Gains Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| CG-009 | **Year-End Gain/Loss Review** | November-December | "Review realized gains YTD: ${gains}. Consider harvesting ${losses} to offset." |
| CG-010 | **$3,000 Loss Deduction** | Net Capital Loss > $3,000 | "Capital losses exceed gains by ${excess}. Only $3,000 deductible this year. Remainder carries forward." |
| CG-011 | **Mutual Fund Distribution Warning** | November-December AND Holds Mutual Funds | "Check for upcoming mutual fund capital gains distributions before year-end." |

---

## 4. Equity Compensation Alerts (14)

### 4.1 RSU Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| EQ-001 | **RSU Double-Count Risk** | RSU Sold via Sell-to-Cover AND 1099-B Shows $0 Basis | "Your 1099-B may show $0 cost basis for RSU shares. Actual basis is ${basis}. Adjust to avoid double taxation." |
| EQ-002 | **Large RSU Vest Upcoming** | RSU Vest > $50,000 within 30 days | "${shares} shares (${value}) vesting on {date}. Plan for ${tax_estimate} in withholding." |
| EQ-003 | **RSU Concentration Risk** | RSU Value > 30% of Net Worth | "RSU concentration at {percent}%. Consider selling vested shares to diversify." |
| EQ-004 | **Multi-State RSU Sourcing** | Changed State AND Has Unvested RSUs from Prior State | "RSUs granted in {prior_state} may be taxable there even after moving. {percent}% sourced to {prior_state}." |

### 4.2 ISO Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| EQ-005 | **ISO Expiration Warning** | ISOs Expiring within 90 days | "{shares} ISOs expiring on {date}. Strike price: ${strike}. Current price: ${current}. Value: ${value}." |
| EQ-006 | **ISO Qualifying Disposition Date** | ISO Shares approaching qualifying date | "ISO shares from {exercise_date} become qualifying on {qualifying_date} ({days} days). Hold to convert to LTCG." |
| EQ-007 | **ISO Disqualifying Sale Warning** | Sale of ISO shares before qualifying | "Selling these ISO shares before {date} triggers disqualifying disposition. ${ordinary_income} taxed as ordinary income." |
| EQ-008 | **ISO Exercise Window** | Left Company AND Exercise Window < 90 days | "You have {days} days to exercise {shares} ISOs before they expire. Evaluate exercise vs. forfeit." |

### 4.3 ESPP Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| EQ-009 | **ESPP Qualifying Date** | ESPP Shares approaching qualifying date | "ESPP shares purchased {purchase_date} become qualifying on {qualifying_date}. Hold for better tax treatment." |
| EQ-010 | **ESPP Disqualifying Sale Warning** | ESPP sale before qualifying | "Selling ESPP before {date} is disqualifying. ${ordinary_income} taxed as ordinary income instead of LTCG." |
| EQ-011 | **ESPP Enrollment Reminder** | ESPP Enrollment Period Starting | "ESPP enrollment opens {date}. 15% discount on lower of offering/purchase price." |

### 4.4 General Equity Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| EQ-012 | **10b5-1 Trading Window** | Has Company Stock AND Trading Window Alert | "Trading window opens {date}. Review equity sale opportunities." |
| EQ-013 | **Form 3921/3922 Required** | ISO Exercise OR ESPP Purchase | "Expect Form {form} from employer. Needed for accurate tax reporting." |
| EQ-014 | **Equity to Cash Ratio** | Equity > 80% of liquid assets | "Equity is {percent}% of liquid assets. Consider diversifying for liquidity." |

---

## 5. State Tax Alerts (8)

### 5.1 California Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| ST-001 | **CA Mental Health Services Tax** | CA Resident AND Income > $1M | "Income over $1M triggers 1% Mental Health Services Tax. Additional ${tax} owed." |
| ST-002 | **CA SDI Uncapped** | CA Resident AND High Income | "CA SDI now uncapped. ${sdi_tax} SDI tax on ${income} income." |
| ST-003 | **CA Phantom RSU Income** | Moved from CA AND Has Unvested CA RSUs | "California may tax ${amount} of RSU income sourced to your CA work period." |

### 5.2 New York Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| ST-004 | **NYC City Tax** | NYC Resident | "NYC city tax adds 3.078%-3.876% on top of NY state tax. Combined rate: {rate}%." |
| ST-005 | **NY Convenience Rule** | Remote Worker for NY Employer | "NY 'convenience of employer' rule may require filing NY taxes despite living in {state}." |

### 5.3 Washington Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| ST-006 | **WA Cap Gains Approaching Threshold** | WA Resident AND LTCG > $200,000 | "Long-term gains approaching WA threshold (${threshold}). ${remaining} remaining before 7% tax applies." |
| ST-007 | **WA Cap Gains 9.9% Tier** | WA Resident AND LTCG > $1M + Deduction | "Long-term gains over $1M subject to 9.9% rate. Consider spreading sales across years." |

### 5.4 Multi-State Alert

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| ST-008 | **Multi-State Filing Required** | Earned Income in Multiple States | "You may owe taxes in {states}. Review state sourcing for W-2 and equity income." |

---

## 6. Retirement & Savings Alerts (6)

### 6.1 401(k) Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| RT-001 | **401(k) Max Not Met** | YTD 401(k) < Max AND Days Remaining | "You've contributed ${contributed}. Max is ${max}. Increase to ${per_paycheck}/paycheck to max out." |
| RT-002 | **Catch-Up Eligible** | Age >= 50 AND Not Using Catch-Up | "You're eligible for $7,500 catch-up contribution. Total max: ${total_max}." |
| RT-003 | **Mega Backdoor Roth Available** | Employer Allows After-Tax 401(k) | "Your plan allows after-tax contributions. Consider mega backdoor Roth for additional ${available}." |

### 6.2 HSA Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| RT-004 | **HSA Max Not Met** | Has HDHP AND YTD HSA < Max | "HSA contribution: ${contributed}. Max: ${max}. Triple tax advantage - consider maxing out." |
| RT-005 | **HSA Family Limit Change** | Changed Coverage Mid-Year | "Mid-year coverage change affects HSA limit. Pro-rated max: ${prorated}." |

### 6.3 IRA Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| RT-006 | **Backdoor Roth Opportunity** | High Income AND No IRA Contribution | "Income too high for Roth? Consider backdoor Roth IRA (max ${max})." |

---

## 7. Year-End Planning Alerts (7)

### 7.1 Deadline Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| YE-001 | **Tax-Loss Harvesting Deadline** | December 1-31 | "Last chance to harvest losses for {year}. Trades must settle by Dec 31." |
| YE-002 | **Charitable Giving Deadline** | December | "Charitable contributions must be made by Dec 31 for {year} deduction." |
| YE-003 | **RSU Vest Year-End** | RSU Vesting in December | "December RSU vest counts as {year} income. January vest defers to {next_year}." |

### 7.2 Strategy Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| YE-004 | **Defer Income to Next Year** | Expecting Lower Income Next Year | "Consider deferring ${amount} to {next_year} if expecting lower income." |
| YE-005 | **Accelerate Income** | Expecting Higher Income Next Year | "Consider accelerating income to {year}. Lower bracket this year." |
| YE-006 | **Bunch Deductions** | Itemized Deductions Near Standard | "Consider bunching charitable donations. ${current} deductions vs ${standard} standard." |
| YE-007 | **Required Minimum Distribution** | Age >= 73 AND Has Traditional IRA/401(k) | "RMD of ${rmd} due by Dec 31. Failure triggers 25% penalty." |

---

## 8. Additional Alerts (5)

### 8.1 Compliance Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| CM-001 | **Estimated Payment Deadline** | Approaching Q1/Q2/Q3/Q4 deadline | "Q{quarter} estimated tax due {date}. Suggested payment: ${amount}." |
| CM-002 | **Extension Filed Reminder** | Filed Extension | "Extension gives until Oct 15 to file, but taxes were due April 15. Interest accruing on ${owed}." |

### 8.2 Opportunity Alerts

| ID | Alert Name | Trigger Condition | Message Template |
|----|------------|-------------------|------------------|
| OP-001 | **Tax Bracket Optimization** | Income Near Bracket Boundary | "You're ${delta} from the {rate}% bracket. Consider Roth conversion or income deferral." |
| OP-002 | **Charitable Stock Donation** | Appreciated Stock AND Charitable Intent | "Donate appreciated stock instead of cash. Avoid ${cap_gains} in capital gains tax." |
| OP-003 | **Donor-Advised Fund** | High Income Year | "Bunch charitable giving into DAF for {year} deduction. Distribute over time." |

---

## 9. Alert Implementation

### 9.1 Alert Data Model

```python
class TaxAlert(BaseModel):
    """Red flag alert definition."""

    alert_id: str  # e.g., "UW-001"
    category: AlertCategory
    priority: Literal["CRITICAL", "WARNING", "INFO"]
    title: str
    message_template: str
    trigger_conditions: List[AlertCondition]
    action_items: List[str]
    deadline: Optional[date]
    dismissed: bool = False
    created_at: datetime
    expires_at: Optional[datetime]


class AlertCondition(BaseModel):
    """Single condition for triggering an alert."""

    field: str  # e.g., "estimated_tax_gap"
    operator: Literal["gt", "lt", "eq", "gte", "lte", "between"]
    value: Union[Decimal, int, str, List]
    and_conditions: Optional[List["AlertCondition"]]
    or_conditions: Optional[List["AlertCondition"]]


class AlertCategory(str, Enum):
    UNDERWITHHOLDING = "underwithholding"
    AMT = "amt"
    CAPITAL_GAINS = "capital_gains"
    EQUITY_COMP = "equity_compensation"
    STATE_TAX = "state_tax"
    RETIREMENT = "retirement"
    YEAR_END = "year_end"
    COMPLIANCE = "compliance"
    OPPORTUNITY = "opportunity"
```

### 9.2 Alert Engine

```python
class AlertEngine:
    """Engine for evaluating and generating alerts."""

    def __init__(self, alert_definitions: List[AlertDefinition]):
        self.definitions = {a.alert_id: a for a in alert_definitions}

    def evaluate_all(self, user_data: UserFinancialData) -> List[TaxAlert]:
        """Evaluate all alert conditions against user data."""
        alerts = []

        for definition in self.definitions.values():
            if self._evaluate_conditions(definition.trigger_conditions, user_data):
                alert = self._create_alert(definition, user_data)
                alerts.append(alert)

        return sorted(alerts, key=lambda a: (
            0 if a.priority == "CRITICAL" else 1 if a.priority == "WARNING" else 2,
            a.deadline or date.max
        ))

    def _evaluate_conditions(
        self,
        conditions: List[AlertCondition],
        user_data: UserFinancialData
    ) -> bool:
        """Evaluate if all conditions are met."""
        for condition in conditions:
            value = self._get_field_value(user_data, condition.field)

            if not self._compare(value, condition.operator, condition.value):
                return False

            if condition.and_conditions:
                if not self._evaluate_conditions(condition.and_conditions, user_data):
                    return False

        return True

    def _create_alert(
        self,
        definition: AlertDefinition,
        user_data: UserFinancialData
    ) -> TaxAlert:
        """Create alert with populated message template."""
        message = self._populate_template(definition.message_template, user_data)

        return TaxAlert(
            alert_id=definition.alert_id,
            category=definition.category,
            priority=definition.priority,
            title=definition.title,
            message_template=message,
            trigger_conditions=definition.trigger_conditions,
            action_items=definition.action_items,
            deadline=self._calculate_deadline(definition, user_data),
            created_at=datetime.now(),
        )
```

### 9.3 Alert Refresh Schedule

| Trigger | Alerts Evaluated | Frequency |
|---------|------------------|-----------|
| Data sync (Plaid) | All | Daily |
| Document upload | Income, Withholding | On upload |
| Manual data change | Affected alerts | On change |
| Transaction detected | Capital gains, Wash sale | Real-time |
| Date-based | Year-end, Deadlines | Daily |

### 9.4 Alert Priority by User Impact

| Priority | Criteria | User Action |
|----------|----------|-------------|
| CRITICAL | Financial impact > $10,000 OR Deadline < 7 days | Push notification, email |
| WARNING | Financial impact $1,000-$10,000 OR Deadline < 30 days | Dashboard highlight |
| INFO | Optimization opportunity OR Awareness | Dashboard display |

---

## 10. Alert Summary by Category

| Category | Critical | Warning | Info | Total |
|----------|----------|---------|------|-------|
| Underwithholding | 3 | 5 | 4 | 12 |
| AMT | 3 | 4 | 3 | 10 |
| Capital Gains | 3 | 5 | 3 | 11 |
| Equity Compensation | 0 | 8 | 6 | 14 |
| State Tax | 2 | 4 | 2 | 8 |
| Retirement & Savings | 0 | 3 | 3 | 6 |
| Year-End Planning | 1 | 3 | 3 | 7 |
| Additional | 0 | 2 | 3 | 5 |
| **TOTAL** | **12** | **34** | **27** | **73** |

---

## 11. Sources

### Tax Planning Resources
- IRS Publication 505: Tax Withholding and Estimated Tax
- IRS Form 6251: Alternative Minimum Tax
- IRS Schedule D: Capital Gains and Losses
- IRS Publication 550: Investment Income and Expenses

### Equity Compensation
- myStockOptions.com: Equity Compensation Education
- NCEO: Employee Stock Options Guide
- Fidelity: Equity Compensation Tax Guide

### State Tax
- California FTB: Nonresident Withholding
- New York DTF: Convenience of Employer Rule
- Washington DOR: Capital Gains Tax

### Industry Research
- Betterment: Tax-Loss Harvesting Research
- Wealthfront: Tax-Loss Harvesting White Paper
- Vanguard: Tax-Loss Harvesting Guide

---

*Document generated as part of TaxLens Phase 1 Research*
