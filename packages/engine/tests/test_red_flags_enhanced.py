"""
Tests for enhanced red flags system.

Tests cover:
- Estimated payment deadline tracking
- Quarterly underwithholding analysis
- State nexus warnings
- Wash sale detection
- Alert prioritization
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from taxlens_engine.red_flags_enhanced import (
    EstimatedPaymentDeadline,
    check_estimated_payment_deadlines,
    check_quarterly_underwithholding,
    StatePresence,
    StateNexusType,
    check_state_nexus,
    NO_INCOME_TAX_STATES,
    StockTransaction,
    WashSaleViolation,
    detect_wash_sales,
    AlertPriority,
    calculate_alert_priority,
    prioritize_alerts,
    analyze_red_flags_enhanced,
)
from taxlens_engine.red_flags import TaxAlert, AlertSeverity, AlertCategory


# ============================================================
# Estimated Payment Deadline Tests
# ============================================================

class TestEstimatedPaymentDeadlines:
    """Tests for estimated payment deadline checking."""
    
    def test_get_deadlines_2025(self):
        """Test deadline generation for 2025."""
        deadlines = EstimatedPaymentDeadline.get_deadlines(2025)
        
        assert len(deadlines) == 4
        assert deadlines[0].quarter == 1
        assert deadlines[0].due_date == date(2025, 4, 15)
        assert deadlines[1].quarter == 2
        assert deadlines[1].due_date == date(2025, 6, 15)
        assert deadlines[2].quarter == 3
        assert deadlines[2].due_date == date(2025, 9, 15)
        assert deadlines[3].quarter == 4
        assert deadlines[3].due_date == date(2026, 1, 15)
    
    def test_upcoming_deadline_warning(self):
        """Test alert when deadline is approaching."""
        current_date = date(2025, 4, 1)  # 14 days before Q1 deadline
        
        alerts = check_estimated_payment_deadlines(
            current_date=current_date,
            estimated_payments_made={},  # Nothing paid yet
            projected_annual_tax=Decimal("40000"),
            prior_year_tax=Decimal("35000"),
        )
        
        # Should warn about upcoming Q1 deadline
        deadline_alerts = [a for a in alerts if "Q1" in a.title and "Due" in a.title]
        assert len(deadline_alerts) == 1
        assert deadline_alerts[0].severity == AlertSeverity.WARNING
        assert "14 days" in deadline_alerts[0].message
    
    def test_critical_when_deadline_imminent(self):
        """Test critical alert when deadline is within 7 days."""
        current_date = date(2025, 4, 10)  # 5 days before Q1 deadline
        
        alerts = check_estimated_payment_deadlines(
            current_date=current_date,
            estimated_payments_made={},
            projected_annual_tax=Decimal("40000"),
        )
        
        deadline_alerts = [a for a in alerts if "Q1" in a.title and "Due" in a.title]
        assert len(deadline_alerts) == 1
        assert deadline_alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_no_alert_when_payment_made(self):
        """Test no alert when quarterly payment already made."""
        current_date = date(2025, 4, 1)
        required = Decimal("10000")  # Assuming 40K annual / 4
        
        alerts = check_estimated_payment_deadlines(
            current_date=current_date,
            estimated_payments_made={1: required},  # Q1 paid
            projected_annual_tax=Decimal("40000"),
        )
        
        # Should have info alert saying on track
        on_track = [a for a in alerts if "On Track" in a.title]
        assert len(on_track) == 1
        assert on_track[0].severity == AlertSeverity.INFO
    
    def test_missed_payment_warning(self):
        """Test warning for missed past deadline."""
        current_date = date(2025, 5, 1)  # After Q1 deadline
        
        alerts = check_estimated_payment_deadlines(
            current_date=current_date,
            estimated_payments_made={1: Decimal("2000")},  # Only $2K paid
            projected_annual_tax=Decimal("40000"),
            prior_year_tax=Decimal("36000"),
        )
        
        missed = [a for a in alerts if "Q1" in a.title and "Short" in a.title]
        assert len(missed) == 1
        assert missed[0].severity == AlertSeverity.WARNING


# ============================================================
# Quarterly Underwithholding Tests
# ============================================================

class TestQuarterlyUnderwithholding:
    """Tests for quarterly underwithholding checks."""
    
    def test_on_pace_no_alert(self):
        """Test no warning when withholding is on pace."""
        current_date = date(2025, 6, 30)  # Mid-year
        
        alerts = check_quarterly_underwithholding(
            current_date=current_date,
            ytd_income=Decimal("125000"),  # Half of annual
            ytd_withheld=Decimal("25000"),  # Half of annual tax
            projected_annual_income=Decimal("250000"),
            projected_annual_tax=Decimal("50000"),
        )
        
        # Should not have underwithholding warning
        underwithheld = [a for a in alerts if "Underwithholding" in a.title]
        assert len(underwithheld) == 0
    
    def test_behind_pace_warning(self):
        """Test warning when withholding is moderately behind pace."""
        current_date = date(2025, 6, 30)  # Mid-year
        
        alerts = check_quarterly_underwithholding(
            current_date=current_date,
            ytd_income=Decimal("125000"),
            ytd_withheld=Decimal("22000"),  # 22K withheld, expect 25K (3K short)
            projected_annual_income=Decimal("250000"),
            projected_annual_tax=Decimal("50000"),
        )
        
        underwithheld = [a for a in alerts if "Underwithholding" in a.title]
        assert len(underwithheld) == 1
        assert underwithheld[0].severity == AlertSeverity.WARNING
    
    def test_critical_when_far_behind(self):
        """Test critical alert when significantly behind."""
        current_date = date(2025, 6, 30)
        
        alerts = check_quarterly_underwithholding(
            current_date=current_date,
            ytd_income=Decimal("200000"),  # High income
            ytd_withheld=Decimal("10000"),  # Very little withheld
            projected_annual_income=Decimal("400000"),
            projected_annual_tax=Decimal("100000"),
        )
        
        underwithheld = [a for a in alerts if "Underwithholding" in a.title]
        assert len(underwithheld) == 1
        assert underwithheld[0].severity == AlertSeverity.CRITICAL
    
    def test_income_ahead_of_projections(self):
        """Test info alert when income is ahead of projections."""
        current_date = date(2025, 3, 31)  # End of Q1
        
        alerts = check_quarterly_underwithholding(
            current_date=current_date,
            ytd_income=Decimal("100000"),  # 40% of annual in 25% of year
            ytd_withheld=Decimal("25000"),
            projected_annual_income=Decimal("250000"),
            projected_annual_tax=Decimal("50000"),
        )
        
        ahead = [a for a in alerts if "Ahead" in a.title]
        assert len(ahead) == 1
        assert ahead[0].severity == AlertSeverity.INFO


# ============================================================
# State Nexus Tests
# ============================================================

class TestStateNexus:
    """Tests for state nexus warnings."""
    
    def test_no_alerts_same_state(self):
        """No alerts when only in primary state."""
        alerts = check_state_nexus(
            primary_state="CA",
            other_state_presence=[
                StatePresence(state_code="CA", days_present=365)
            ],
            total_income=Decimal("300000"),
        )
        
        assert len(alerts) == 0
    
    def test_residency_threshold_exceeded(self):
        """Alert when residency threshold exceeded."""
        alerts = check_state_nexus(
            primary_state="CA",
            other_state_presence=[
                StatePresence(state_code="NY", days_present=200)  # > 183 days
            ],
            total_income=Decimal("300000"),
        )
        
        residency_alerts = [a for a in alerts if "Residency" in a.title and "Triggered" in a.title]
        assert len(residency_alerts) == 1
        assert residency_alerts[0].severity == AlertSeverity.CRITICAL
        assert "NY" in residency_alerts[0].message
    
    def test_approaching_threshold_warning(self):
        """Warning when approaching residency threshold."""
        alerts = check_state_nexus(
            primary_state="CA",
            other_state_presence=[
                StatePresence(state_code="NY", days_present=160)  # < 183 but close
            ],
            total_income=Decimal("300000"),
        )
        
        approaching = [a for a in alerts if "Approaching" in a.title]
        assert len(approaching) == 1
        assert approaching[0].severity == AlertSeverity.WARNING
    
    def test_work_days_in_other_state(self):
        """Alert for work performed in another state."""
        alerts = check_state_nexus(
            primary_state="CA",
            other_state_presence=[
                StatePresence(
                    state_code="NY",
                    days_present=50,
                    days_worked=40,
                    income_earned=Decimal("50000"),
                )
            ],
            total_income=Decimal("300000"),
        )
        
        work_alerts = [a for a in alerts if "Non-Resident" in a.title]
        assert len(work_alerts) == 1
        assert "40 days" in work_alerts[0].message
    
    def test_no_income_tax_state(self):
        """Info alert for extended presence in no-income-tax state."""
        alerts = check_state_nexus(
            primary_state="CA",
            other_state_presence=[
                StatePresence(state_code="WA", days_present=200)
            ],
            total_income=Decimal("300000"),
        )
        
        # Should be info level, not critical
        wa_alerts = [a for a in alerts if "WA" in a.title]
        assert len(wa_alerts) == 1
        assert wa_alerts[0].severity == AlertSeverity.INFO
    
    def test_multiple_primary_residences(self):
        """Alert for multiple primary residences (mid-year move)."""
        alerts = check_state_nexus(
            primary_state="CA",
            other_state_presence=[
                StatePresence(
                    state_code="NY",
                    days_present=180,
                    is_primary_residence=True,
                )
            ],
            total_income=Decimal("300000"),
        )
        
        multi = [a for a in alerts if "Multiple" in a.title]
        assert len(multi) == 1
        assert "part-year" in multi[0].action_required.lower()


# ============================================================
# Wash Sale Detection Tests
# ============================================================

class TestWashSaleDetection:
    """Tests for wash sale detection."""
    
    def test_no_wash_sale(self):
        """No alert when sales have gains or no rebuy."""
        transactions = [
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("150"),
            ),
            StockTransaction(
                date=date(2025, 6, 15),  # > 30 days later
                symbol="AAPL",
                action="sell",
                shares=Decimal("100"),
                price=Decimal("180"),  # Gain, not loss
            ),
        ]
        
        alerts = detect_wash_sales(transactions)
        wash_alerts = [a for a in alerts if "Wash Sale" in a.title]
        assert len(wash_alerts) == 0
    
    def test_wash_sale_buy_after_sell(self):
        """Detect wash sale when buying after selling at loss."""
        transactions = [
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("180"),
            ),
            StockTransaction(
                date=date(2025, 3, 15),
                symbol="AAPL",
                action="sell",
                shares=Decimal("100"),
                price=Decimal("150"),  # Loss of $30/share
            ),
            StockTransaction(
                date=date(2025, 3, 25),  # 10 days after sell
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("155"),
            ),
        ]
        
        alerts = detect_wash_sales(transactions)
        wash_alerts = [a for a in alerts if "Wash Sale Detected" in a.title]
        assert len(wash_alerts) == 1
        assert "AAPL" in wash_alerts[0].message
        assert "10 days apart" in wash_alerts[0].message
    
    def test_wash_sale_buy_before_sell(self):
        """Detect wash sale when buying before selling at loss."""
        transactions = [
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="GOOG",
                action="buy",
                shares=Decimal("50"),
                price=Decimal("200"),
            ),
            StockTransaction(
                date=date(2025, 3, 1),  # Buy replacement first
                symbol="GOOG",
                action="buy",
                shares=Decimal("50"),
                price=Decimal("160"),
            ),
            StockTransaction(
                date=date(2025, 3, 15),  # Then sell at loss
                symbol="GOOG",
                action="sell",
                shares=Decimal("50"),
                price=Decimal("150"),  # Loss vs $200 cost
            ),
        ]
        
        alerts = detect_wash_sales(transactions)
        wash_alerts = [a for a in alerts if "Wash Sale Detected" in a.title]
        assert len(wash_alerts) == 1
        assert "before" in wash_alerts[0].message
    
    def test_no_wash_sale_outside_window(self):
        """No wash sale if rebuy is > 30 days out."""
        transactions = [
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("180"),
            ),
            StockTransaction(
                date=date(2025, 3, 15),
                symbol="AAPL",
                action="sell",
                shares=Decimal("100"),
                price=Decimal("150"),
            ),
            StockTransaction(
                date=date(2025, 4, 20),  # 36 days later - outside window
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("155"),
            ),
        ]
        
        alerts = detect_wash_sales(transactions)
        wash_alerts = [a for a in alerts if "Wash Sale Detected" in a.title]
        assert len(wash_alerts) == 0
    
    def test_different_symbols_no_wash(self):
        """No wash sale for different symbols."""
        transactions = [
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("180"),
            ),
            StockTransaction(
                date=date(2025, 3, 15),
                symbol="AAPL",
                action="sell",
                shares=Decimal("100"),
                price=Decimal("150"),
            ),
            StockTransaction(
                date=date(2025, 3, 20),
                symbol="GOOG",  # Different symbol
                action="buy",
                shares=Decimal("50"),
                price=Decimal("100"),
            ),
        ]
        
        alerts = detect_wash_sales(transactions)
        wash_alerts = [a for a in alerts if "Wash Sale Detected" in a.title]
        assert len(wash_alerts) == 0
    
    def test_partial_wash_sale(self):
        """Wash sale on partial shares."""
        transactions = [
            StockTransaction(
                date=date(2025, 1, 15),
                symbol="AAPL",
                action="buy",
                shares=Decimal("100"),
                price=Decimal("180"),
            ),
            StockTransaction(
                date=date(2025, 3, 15),
                symbol="AAPL",
                action="sell",
                shares=Decimal("100"),
                price=Decimal("150"),
            ),
            StockTransaction(
                date=date(2025, 3, 20),
                symbol="AAPL",
                action="buy",
                shares=Decimal("50"),  # Only 50 shares
                price=Decimal("155"),
            ),
        ]
        
        alerts = detect_wash_sales(transactions)
        wash_alerts = [a for a in alerts if "Wash Sale Detected" in a.title]
        assert len(wash_alerts) == 1
        # Should show 50 shares affected
        assert "50" in wash_alerts[0].message


# ============================================================
# Alert Priority Tests
# ============================================================

class TestAlertPriority:
    """Tests for alert prioritization."""
    
    def test_critical_always_immediate(self):
        """Critical alerts are always immediate priority."""
        alert = TaxAlert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.WITHHOLDING,
            title="Critical Issue",
            message="Something critical",
        )
        
        priority = calculate_alert_priority(alert, date(2025, 1, 15))
        assert priority == AlertPriority.IMMEDIATE
    
    def test_deadline_based_priority(self):
        """Priority based on deadline proximity."""
        # Deadline in 5 days
        alert_soon = TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.ESTIMATED_PAYMENTS,
            title="Payment Due",
            message="Payment due soon",
            deadline="2025-01-20",
        )
        
        priority = calculate_alert_priority(alert_soon, date(2025, 1, 15))
        assert priority == AlertPriority.THIS_WEEK
        
        # Deadline in 20 days
        alert_later = TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.ESTIMATED_PAYMENTS,
            title="Payment Due",
            message="Payment due later",
            deadline="2025-02-05",
        )
        
        priority = calculate_alert_priority(alert_later, date(2025, 1, 15))
        assert priority == AlertPriority.THIS_MONTH
    
    def test_amount_based_priority(self):
        """Priority based on amount for warnings."""
        # Large amount
        alert_large = TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.WITHHOLDING,
            title="Large Issue",
            message="Large amount",
            amount=Decimal("10000"),
        )
        
        priority = calculate_alert_priority(alert_large, date(2025, 1, 15))
        assert priority == AlertPriority.THIS_WEEK
        
        # Small amount
        alert_small = TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.WITHHOLDING,
            title="Small Issue",
            message="Small amount",
            amount=Decimal("500"),
        )
        
        priority = calculate_alert_priority(alert_small, date(2025, 1, 15))
        assert priority == AlertPriority.PLANNING
    
    def test_prioritize_alerts_sorting(self):
        """Test that alerts are sorted by priority."""
        alerts = [
            TaxAlert(
                severity=AlertSeverity.INFO,
                category=AlertCategory.PLANNING,
                title="Info",
                message="Low priority",
            ),
            TaxAlert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.WITHHOLDING,
                title="Critical",
                message="Highest priority",
            ),
            TaxAlert(
                severity=AlertSeverity.WARNING,
                category=AlertCategory.ESTIMATED_PAYMENTS,
                title="Warning",
                message="Medium priority",
                deadline="2025-01-20",
            ),
        ]
        
        prioritized = prioritize_alerts(alerts, date(2025, 1, 15))
        
        # First should be critical (immediate)
        assert prioritized[0][0] == AlertPriority.IMMEDIATE
        assert prioritized[0][1].title == "Critical"


# ============================================================
# Integration Tests
# ============================================================

class TestEnhancedAnalysis:
    """Integration tests for enhanced analysis."""
    
    def test_comprehensive_scenario(self):
        """Test comprehensive enhanced analysis."""
        current_date = date(2025, 6, 1)  # June 1
        
        report = analyze_red_flags_enhanced(
            current_date=current_date,
            total_income=Decimal("400000"),
            total_tax_liability=Decimal("100000"),
            total_withheld=Decimal("30000"),
            ytd_income=Decimal("200000"),
            ytd_withheld=Decimal("30000"),
            estimated_payments_made={1: Decimal("10000"), 2: Decimal("5000")},
            primary_state="CA",
            other_state_presence=[
                StatePresence(
                    state_code="NY",
                    days_present=50,
                    days_worked=30,
                    income_earned=Decimal("40000"),
                )
            ],
            stock_transactions=[
                StockTransaction(
                    date=date(2025, 4, 1),
                    symbol="AAPL",
                    action="buy",
                    shares=Decimal("100"),
                    price=Decimal("180"),
                ),
                StockTransaction(
                    date=date(2025, 5, 15),
                    symbol="AAPL",
                    action="sell",
                    shares=Decimal("100"),
                    price=Decimal("150"),
                ),
                StockTransaction(
                    date=date(2025, 5, 25),
                    symbol="AAPL",
                    action="buy",
                    shares=Decimal("100"),
                    price=Decimal("155"),
                ),
            ],
            long_term_gains=Decimal("50000"),
            rsu_income=Decimal("100000"),
            filing_status="single",
            prior_year_tax=Decimal("80000"),
        )
        
        # Should have multiple alerts
        assert len(report.alerts) > 0
        
        # Should have underwithholding warning
        underwithheld = [a for a in report.alerts if "Underwithholding" in a.title]
        assert len(underwithheld) > 0
        
        # Should have NY work day warning
        ny_alerts = [a for a in report.alerts if "NY" in a.message]
        assert len(ny_alerts) > 0
        
        # Should have wash sale warning
        wash_alerts = [a for a in report.alerts if "Wash Sale" in a.title]
        assert len(wash_alerts) > 0
    
    def test_clean_scenario(self):
        """Test scenario with minimal issues."""
        current_date = date(2025, 6, 1)
        
        report = analyze_red_flags_enhanced(
            current_date=current_date,
            total_income=Decimal("150000"),
            total_tax_liability=Decimal("30000"),
            total_withheld=Decimal("15000"),
            ytd_income=Decimal("75000"),
            ytd_withheld=Decimal("15000"),
            estimated_payments_made={1: Decimal("7500"), 2: Decimal("7500")},
            primary_state="CA",
            filing_status="single",
            prior_year_tax=Decimal("28000"),
        )
        
        # Should still have report
        assert report is not None
        # Most alerts should be INFO level
        critical = [a for a in report.alerts if a.severity == AlertSeverity.CRITICAL]
        assert len(critical) == 0
