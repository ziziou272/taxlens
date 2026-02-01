"""
Tests for red flags / warning system.

Tests cover:
- Underwithholding detection
- AMT trigger warnings
- State-specific thresholds
- NIIT checks
- Estimated payment requirements
"""

from decimal import Decimal
import pytest

from taxlens_engine.red_flags import (
    AlertSeverity,
    AlertCategory,
    TaxAlert,
    RedFlagReport,
    check_underwithholding,
    check_rsu_underwithholding,
    check_amt_trigger,
    check_washington_capital_gains,
    check_niit_threshold,
    check_estimated_payments_required,
    analyze_red_flags,
)


class TestUnderwithholding:
    """Test underwithholding checks."""
    
    def test_no_underwithholding(self):
        """No alerts when withheld >= owed."""
        alerts = check_underwithholding(
            total_tax_liability=Decimal("50000"),
            total_withheld=Decimal("52000"),  # Refund
        )
        
        # Should be empty (no underwithholding)
        assert len(alerts) == 0
    
    def test_small_balance_due(self):
        """Small balance due under $1,000."""
        alerts = check_underwithholding(
            total_tax_liability=Decimal("50000"),
            total_withheld=Decimal("49500"),  # $500 due
        )
        
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.INFO
        assert alerts[0].amount == Decimal("500")
    
    def test_significant_underwithholding(self):
        """Significant underwithholding (<90%)."""
        alerts = check_underwithholding(
            total_tax_liability=Decimal("100000"),
            total_withheld=Decimal("80000"),  # 80% = $20K due
        )
        
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        assert len(critical_alerts) == 1
        assert critical_alerts[0].amount == Decimal("20000")
    
    def test_prior_year_safe_harbor_met(self):
        """Prior year safe harbor met."""
        alerts = check_underwithholding(
            total_tax_liability=Decimal("100000"),
            total_withheld=Decimal("85000"),
            prior_year_tax=Decimal("80000"),  # Withheld > prior year
        )
        
        # Should have info alert about safe harbor
        info_alerts = [a for a in alerts if a.severity == AlertSeverity.INFO]
        safe_harbor_alerts = [a for a in info_alerts if "Safe Harbor" in a.title]
        assert len(safe_harbor_alerts) == 1


class TestRSUUnderwithholding:
    """Test RSU-specific underwithholding checks."""
    
    def test_rsu_withholding_gap(self):
        """RSU withholding lower than marginal rate."""
        alerts = check_rsu_underwithholding(
            rsu_income=Decimal("150000"),
            supplemental_withheld=Decimal("60000"),  # ~40%
            actual_marginal_rate=Decimal("0.50"),  # 50% marginal
            state="CA",
        )
        
        assert len(alerts) == 1
        assert alerts[0].category == AlertCategory.WITHHOLDING
        assert "RSU" in alerts[0].title
    
    def test_no_rsu_income(self):
        """No alerts when no RSU income."""
        alerts = check_rsu_underwithholding(
            rsu_income=Decimal("0"),
            supplemental_withheld=Decimal("0"),
            actual_marginal_rate=Decimal("0.45"),
        )
        
        assert len(alerts) == 0


class TestAMTTrigger:
    """Test AMT trigger warnings."""
    
    def test_no_iso_no_amt(self):
        """No AMT alert without ISO."""
        alerts = check_amt_trigger(
            regular_taxable_income=Decimal("200000"),
            iso_bargain_element=Decimal("0"),
        )
        
        assert len(alerts) == 0
    
    def test_small_iso_warning(self):
        """Small ISO creates warning."""
        alerts = check_amt_trigger(
            regular_taxable_income=Decimal("200000"),
            iso_bargain_element=Decimal("50000"),
        )
        
        assert len(alerts) >= 1
        assert any(a.category == AlertCategory.AMT for a in alerts)
    
    def test_large_iso_critical(self):
        """Large ISO creates critical alert."""
        alerts = check_amt_trigger(
            regular_taxable_income=Decimal("200000"),
            iso_bargain_element=Decimal("200000"),
        )
        
        critical = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        assert len(critical) >= 1
        assert "AMT" in critical[0].title
    
    def test_amt_trap_warning(self):
        """Large ISO triggers AMT trap warning."""
        alerts = check_amt_trigger(
            regular_taxable_income=Decimal("200000"),
            iso_bargain_element=Decimal("100000"),
        )
        
        trap_alerts = [a for a in alerts if "Trap" in a.title]
        assert len(trap_alerts) == 1


class TestWashingtonCapitalGains:
    """Test Washington State capital gains threshold."""
    
    def test_under_threshold(self):
        """LTCG under WA threshold."""
        alerts = check_washington_capital_gains(Decimal("200000"))
        
        assert len(alerts) == 0
    
    def test_approaching_threshold(self):
        """LTCG approaching WA threshold."""
        alerts = check_washington_capital_gains(Decimal("250000"))
        
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.INFO
        assert "Approaching" in alerts[0].title
    
    def test_over_threshold(self):
        """LTCG over WA threshold triggers tax."""
        alerts = check_washington_capital_gains(Decimal("300000"))
        
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].amount > Decimal("0")
        
        # Should be 7% of excess over $262K
        # ($300K - $262K) * 7% = $2,660
        expected_tax = (Decimal("300000") - Decimal("262000")) * Decimal("0.07")
        assert alerts[0].amount == expected_tax


class TestNIIT:
    """Test Net Investment Income Tax checks."""
    
    def test_under_threshold(self):
        """No NIIT under threshold."""
        alerts = check_niit_threshold(
            magi=Decimal("180000"),
            investment_income=Decimal("50000"),
            filing_status="single",
        )
        
        assert len(alerts) == 0
    
    def test_single_over_threshold(self):
        """Single filer over $200K MAGI."""
        alerts = check_niit_threshold(
            magi=Decimal("250000"),
            investment_income=Decimal("100000"),
            filing_status="single",
        )
        
        assert len(alerts) == 1
        assert alerts[0].category == AlertCategory.PLANNING
        assert alerts[0].amount > Decimal("0")
    
    def test_married_over_threshold(self):
        """Married filer over $250K MAGI."""
        alerts = check_niit_threshold(
            magi=Decimal("300000"),
            investment_income=Decimal("80000"),
            filing_status="married_jointly",
        )
        
        assert len(alerts) == 1
        # NIIT = 3.8% of lesser of investment income or excess MAGI
        # Excess = $300K - $250K = $50K
        # NIIT = 3.8% of $50K = $1,900
        assert alerts[0].amount == Decimal("1900.00")


class TestEstimatedPayments:
    """Test estimated payment requirement checks."""
    
    def test_small_balance_no_alert(self):
        """Small balance due doesn't require estimates."""
        alerts = check_estimated_payments_required(
            balance_due=Decimal("500"),
            income_sources={"capital_gains": Decimal("5000")},
        )
        
        assert len(alerts) == 0
    
    def test_large_balance_with_investment_income(self):
        """Large balance with investment income triggers alert."""
        alerts = check_estimated_payments_required(
            balance_due=Decimal("15000"),
            income_sources={"capital_gains": Decimal("50000")},
        )
        
        assert len(alerts) == 1
        assert alerts[0].category == AlertCategory.ESTIMATED_PAYMENTS
        # Quarterly payment suggestion
        assert alerts[0].amount == Decimal("3750.00")  # $15K / 4


class TestRedFlagReport:
    """Test RedFlagReport dataclass."""
    
    def test_empty_report(self):
        """Empty report has no alerts."""
        report = RedFlagReport()
        
        assert len(report.alerts) == 0
        assert report.has_critical is False
    
    def test_add_alerts(self):
        """Add alerts to report."""
        report = RedFlagReport()
        report.add_alert(TaxAlert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.WITHHOLDING,
            title="Test Warning",
            message="Test message",
        ))
        
        assert len(report.alerts) == 1
        assert len(report.warning_alerts) == 1
        assert report.has_critical is False
    
    def test_critical_alerts(self):
        """Critical alerts are identified."""
        report = RedFlagReport()
        report.add_alert(TaxAlert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.AMT,
            title="Critical Issue",
            message="Critical message",
        ))
        
        assert report.has_critical is True
        assert len(report.critical_alerts) == 1


class TestComprehensiveAnalysis:
    """Test comprehensive red flag analysis."""
    
    def test_simple_scenario_no_flags(self):
        """Simple scenario with adequate withholding."""
        report = analyze_red_flags(
            total_income=Decimal("150000"),
            total_tax_liability=Decimal("35000"),
            total_withheld=Decimal("36000"),  # Slight refund
            filing_status="single",
            state="CA",
        )
        
        # Should have no critical or warning alerts
        assert not report.has_critical
        assert "No significant" in report.summary or len(report.warning_alerts) == 0
    
    def test_tech_employee_scenario(self):
        """Tech employee with RSU and capital gains."""
        report = analyze_red_flags(
            total_income=Decimal("500000"),
            total_tax_liability=Decimal("180000"),
            total_withheld=Decimal("150000"),  # $30K underwithholding
            long_term_gains=Decimal("100000"),
            rsu_income=Decimal("150000"),
            filing_status="married_jointly",
            state="CA",
        )
        
        # Should have some warnings
        assert len(report.alerts) > 0
    
    def test_iso_exercise_scenario(self):
        """ISO exercise triggering AMT."""
        report = analyze_red_flags(
            total_income=Decimal("250000"),
            total_tax_liability=Decimal("70000"),
            total_withheld=Decimal("50000"),
            iso_bargain_element=Decimal("200000"),
            filing_status="single",
            state="CA",
        )
        
        # Should have AMT alerts
        amt_alerts = [a for a in report.alerts if a.category == AlertCategory.AMT]
        assert len(amt_alerts) > 0
        assert report.has_critical  # Large ISO is critical
    
    def test_wa_resident_scenario(self):
        """Washington resident with capital gains."""
        report = analyze_red_flags(
            total_income=Decimal("400000"),
            total_tax_liability=Decimal("100000"),
            total_withheld=Decimal("100000"),
            long_term_gains=Decimal("300000"),
            filing_status="single",
            state="WA",
        )
        
        # Should have WA capital gains alert
        wa_alerts = [a for a in report.alerts if "Washington" in a.title]
        assert len(wa_alerts) == 1
    
    def test_summary_generation(self):
        """Summary reflects alert severity."""
        # Critical scenario
        critical_report = analyze_red_flags(
            total_income=Decimal("300000"),
            total_tax_liability=Decimal("100000"),
            total_withheld=Decimal("50000"),  # Severe underwithholding
            iso_bargain_element=Decimal("200000"),
            filing_status="single",
            state="CA",
        )
        
        assert "critical" in critical_report.summary.lower() or "⚠️" in critical_report.summary


class TestAlertSeverity:
    """Test alert severity levels."""
    
    def test_severity_ordering(self):
        """Verify severity values exist."""
        assert AlertSeverity.INFO == "info"
        assert AlertSeverity.WARNING == "warning"
        assert AlertSeverity.CRITICAL == "critical"
    
    def test_category_values(self):
        """Verify category values exist."""
        assert AlertCategory.WITHHOLDING == "withholding"
        assert AlertCategory.AMT == "amt"
        assert AlertCategory.STATE_TAX == "state_tax"
