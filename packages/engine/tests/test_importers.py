"""
Tests for data importers (Fidelity and Schwab).

Tests cover:
- CSV parsing for various formats
- Transaction classification
- Vesting and sale extraction
- Edge cases and error handling
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine.importers import (
    parse_fidelity_csv,
    FidelityTransaction,
    parse_schwab_csv,
    SchwabTransaction,
)
from taxlens_engine.importers.fidelity import (
    FidelityActionType,
    FidelityParseResult,
    extract_vesting_summary,
    extract_sales_summary,
    _parse_date,
    _parse_decimal,
    _classify_action,
)
from taxlens_engine.importers.schwab import (
    SchwabActionType,
    SchwabParseResult,
    extract_tax_lots,
    parse_schwab_gain_loss_report,
    _detect_award_type,
)


# ============================================================
# Fidelity Parser Tests
# ============================================================

class TestFidelityDateParsing:
    """Tests for Fidelity date parsing."""
    
    def test_mm_dd_yyyy(self):
        assert _parse_date("01/15/2025") == date(2025, 1, 15)
    
    def test_yyyy_mm_dd(self):
        assert _parse_date("2025-01-15") == date(2025, 1, 15)
    
    def test_month_name(self):
        assert _parse_date("Jan 15, 2025") == date(2025, 1, 15)
    
    def test_empty_string(self):
        assert _parse_date("") is None
    
    def test_invalid_date(self):
        assert _parse_date("not a date") is None


class TestFidelityDecimalParsing:
    """Tests for Fidelity decimal parsing."""
    
    def test_plain_number(self):
        assert _parse_decimal("100.50") == Decimal("100.50")
    
    def test_currency_symbol(self):
        assert _parse_decimal("$1,234.56") == Decimal("1234.56")
    
    def test_negative_in_parens(self):
        assert _parse_decimal("($500.00)") == Decimal("-500.00")
    
    def test_empty_values(self):
        assert _parse_decimal("") is None
        assert _parse_decimal("-") is None
        assert _parse_decimal("N/A") is None


class TestFidelityActionClassification:
    """Tests for Fidelity action classification."""
    
    def test_deposit_stock(self):
        assert _classify_action("DEPOSIT STOCK") == FidelityActionType.DEPOSIT
    
    def test_sale(self):
        assert _classify_action("SALE") == FidelityActionType.SALE
    
    def test_tax_withhold(self):
        assert _classify_action("TAX WITHHOLD") == FidelityActionType.TAX_WITHHOLD
    
    def test_dividend(self):
        assert _classify_action("DIVIDEND") == FidelityActionType.DIVIDEND
    
    def test_unknown(self):
        assert _classify_action("RANDOM ACTION") == FidelityActionType.UNKNOWN


class TestFidelityCSVParser:
    """Tests for Fidelity CSV parsing."""
    
    def test_basic_csv(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,DEPOSIT STOCK,AAPL,RSU Vesting,100,150.00,15000.00
01/15/2025,SALE,AAPL,Same Day Sale,40,150.00,6000.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert result.success
        assert len(result.transactions) == 2
        assert result.raw_rows == 2
        
        # Check vesting
        assert len(result.vesting_events) == 1
        assert result.vesting_events[0]["shares"] == Decimal("100")
        assert result.vesting_events[0]["fmv"] == Decimal("150.00")
        
        # Check sale
        assert len(result.sales) == 1
        assert result.sales[0]["shares"] == Decimal("40")
    
    def test_symbol_filter(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,DEPOSIT STOCK,AAPL,RSU Vesting,100,150.00,15000.00
01/15/2025,DEPOSIT STOCK,GOOG,RSU Vesting,50,100.00,5000.00"""
        
        result = parse_fidelity_csv(csv_content, symbol_filter="AAPL")
        
        assert len(result.transactions) == 1
        assert result.transactions[0].symbol == "AAPL"
    
    def test_missing_date_error(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
,DEPOSIT STOCK,AAPL,RSU Vesting,100,150.00,15000.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert len(result.errors) > 0
        assert "parse date" in result.errors[0].lower()
    
    def test_cost_basis_and_gain_loss(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount,Cost Basis,Gain/Loss
01/20/2025,SALE,AAPL,Sell Shares,50,200.00,10000.00,7500.00,2500.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert len(result.sales) == 1
        assert result.sales[0]["cost_basis"] == Decimal("7500.00")
        assert result.sales[0]["gain_loss"] == Decimal("2500.00")
    
    def test_empty_csv(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert result.success  # No errors, just empty
        assert len(result.transactions) == 0


class TestFidelitySummaries:
    """Tests for Fidelity summary extraction."""
    
    def test_vesting_summary(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,DEPOSIT STOCK,AAPL,RSU Q1,100,150.00,15000.00
04/15/2025,DEPOSIT STOCK,AAPL,RSU Q2,100,160.00,16000.00"""
        
        result = parse_fidelity_csv(csv_content)
        summary = extract_vesting_summary(result, year=2025)
        
        assert summary["vesting_count"] == 2
        assert summary["total_shares"] == Decimal("200")
        assert summary["total_value"] == Decimal("31000.00")
    
    def test_sales_summary(self):
        csv_content = """Date,Action,Symbol,Quantity,Price,Amount,Cost Basis,Gain/Loss
01/20/2025,SALE,AAPL,50,200.00,10000.00,7500.00,2500.00
02/20/2025,SALE,AAPL,30,210.00,6300.00,4500.00,1800.00"""
        
        result = parse_fidelity_csv(csv_content)
        summary = extract_sales_summary(result, year=2025)
        
        assert summary["sale_count"] == 2
        assert summary["total_shares"] == Decimal("80")
        assert summary["total_proceeds"] == Decimal("16300.00")
        assert summary["total_gain_loss"] == Decimal("4300.00")


# ============================================================
# Schwab Parser Tests
# ============================================================

class TestSchwabActionClassification:
    """Tests for Schwab action classification."""
    
    def test_lapse(self):
        from taxlens_engine.importers.schwab import _classify_action
        assert _classify_action("Lapse") == SchwabActionType.LAPSE
    
    def test_sale(self):
        from taxlens_engine.importers.schwab import _classify_action
        assert _classify_action("Sale") == SchwabActionType.SALE
    
    def test_exercise(self):
        from taxlens_engine.importers.schwab import _classify_action
        assert _classify_action("Exercise") == SchwabActionType.EXERCISE


class TestSchwabAwardTypeDetection:
    """Tests for Schwab award type detection."""
    
    def test_rsu(self):
        assert _detect_award_type("RSU Vesting") == "RSU"
        assert _detect_award_type("Restricted Stock Units") == "RSU"
    
    def test_iso(self):
        assert _detect_award_type("ISO Exercise") == "ISO"
        assert _detect_award_type("Incentive Stock Options") == "ISO"
    
    def test_nso(self):
        assert _detect_award_type("NSO Exercise") == "NSO"
        assert _detect_award_type("Non-Qualified Stock Option") == "NSO"
    
    def test_espp(self):
        assert _detect_award_type("ESPP Purchase") == "ESPP"
    
    def test_unknown(self):
        assert _detect_award_type("Random Transaction") is None


class TestSchwabCSVParser:
    """Tests for Schwab CSV parsing."""
    
    def test_basic_csv(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,Lapse,AAPL,RSU Vesting,100,150.00,15000.00
01/15/2025,Sale,AAPL,Same Day Sale,40,150.00,6000.00"""
        
        result = parse_schwab_csv(csv_content)
        
        assert result.success
        assert len(result.transactions) == 2
        
        # Check vesting
        assert len(result.vesting_events) == 1
        assert result.vesting_events[0]["shares"] == Decimal("100")
        assert result.vesting_events[0]["award_type"] == "RSU"
        
        # Check sale
        assert len(result.sales) == 1
    
    def test_option_exercise(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,Exercise,AAPL,ISO Exercise,500,50.00,25000.00"""
        
        result = parse_schwab_csv(csv_content)
        
        assert len(result.exercises) == 1
        assert result.exercises[0]["shares"] == Decimal("500")
        assert result.exercises[0]["award_type"] == "ISO"
    
    def test_symbol_filter(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2025,Lapse,AAPL,RSU,100,150.00,15000.00
01/15/2025,Lapse,GOOG,RSU,50,100.00,5000.00"""
        
        result = parse_schwab_csv(csv_content, symbol_filter="GOOG")
        
        assert len(result.transactions) == 1
        assert result.transactions[0].symbol == "GOOG"
    
    def test_with_cost_basis(self):
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount,Cost Basis,Gain/Loss,Term
01/20/2025,Sale,AAPL,Sell Shares,50,200.00,10000.00,7500.00,2500.00,Long"""
        
        result = parse_schwab_csv(csv_content)
        
        assert len(result.sales) == 1
        sale = result.sales[0]
        assert sale["cost_basis"] == Decimal("7500.00")
        assert sale["gain_loss"] == Decimal("2500.00")
        assert sale["term"] == "Long"


class TestSchwabTaxLots:
    """Tests for Schwab tax lot extraction."""
    
    def test_separate_short_long(self):
        csv_content = """Date,Action,Symbol,Quantity,Price,Amount,Cost Basis,Gain/Loss,Term,Acquisition Date
01/20/2025,Sale,AAPL,50,200.00,10000.00,7500.00,2500.00,Long,01/01/2024
01/20/2025,Sale,AAPL,30,200.00,6000.00,5500.00,500.00,Short,10/01/2024"""
        
        result = parse_schwab_csv(csv_content)
        tax_lots = extract_tax_lots(result, year=2025)
        
        assert tax_lots["short_term"]["count"] == 1
        assert tax_lots["long_term"]["count"] == 1
        assert tax_lots["long_term"]["gain_loss"] == Decimal("2500.00")
        assert tax_lots["short_term"]["gain_loss"] == Decimal("500.00")
    
    def test_calculate_term_from_dates(self):
        """When term not provided, calculate from dates."""
        csv_content = """Date,Action,Symbol,Quantity,Price,Amount,Cost Basis,Gain/Loss,Acquisition Date
01/20/2025,Sale,AAPL,50,200.00,10000.00,7500.00,2500.00,01/01/2024"""
        
        result = parse_schwab_csv(csv_content)
        tax_lots = extract_tax_lots(result, year=2025)
        
        # 01/01/2024 to 01/20/2025 = 385 days = long term
        assert tax_lots["long_term"]["count"] == 1


class TestSchwabGainLossReport:
    """Tests for specialized Gain/Loss report."""
    
    def test_parse_gain_loss(self):
        csv_content = """Symbol,Sale Date,Acquisition Date,Shares Sold,Proceeds,Cost Basis,Gain/Loss,Term
AAPL,01/20/2025,01/01/2024,100,20000.00,15000.00,5000.00,Long
AAPL,01/20/2025,07/01/2024,50,10000.00,8000.00,2000.00,Short"""
        
        sales = parse_schwab_gain_loss_report(csv_content)
        
        assert len(sales) == 2
        
        long_sale = [s for s in sales if s["term"] == "Long"][0]
        assert long_sale["gain_loss"] == Decimal("5000.00")
        
        short_sale = [s for s in sales if s["term"] == "Short"][0]
        assert short_sale["gain_loss"] == Decimal("2000.00")


# ============================================================
# Edge Cases
# ============================================================

class TestEdgeCases:
    """Edge cases and error handling."""
    
    def test_malformed_csv(self):
        """Handle malformed CSV gracefully."""
        csv_content = "not,a,valid\ncsv,file"
        
        result = parse_fidelity_csv(csv_content)
        # Should not crash, may have errors
        assert isinstance(result, FidelityParseResult)
    
    def test_completely_invalid_data(self):
        """Handle completely invalid data."""
        csv_content = "Date,Action,Symbol,Quantity\nXXX,YYY,ZZZ,ABC"
        
        result = parse_fidelity_csv(csv_content)
        # Date parsing should fail
        assert len(result.errors) > 0
    
    def test_mixed_valid_invalid_rows(self):
        """Process valid rows even if some fail."""
        csv_content = """Date,Action,Symbol,Quantity,Price,Amount
01/15/2025,DEPOSIT STOCK,AAPL,100,150.00,15000.00
INVALID,DEPOSIT STOCK,AAPL,100,150.00,15000.00
01/16/2025,DEPOSIT STOCK,AAPL,100,150.00,15000.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert len(result.transactions) == 2
        assert len(result.errors) == 1  # One invalid row
    
    def test_negative_quantities(self):
        """Handle negative quantities (e.g., tax withholding)."""
        csv_content = """Date,Action,Symbol,Quantity,Price,Amount
01/15/2025,TAX WITHHOLD,AAPL,-40,150.00,-6000.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert len(result.transactions) == 1
        assert result.transactions[0].quantity == Decimal("-40")
    
    def test_zero_values(self):
        """Handle zero values."""
        csv_content = """Date,Action,Symbol,Quantity,Price,Amount
01/15/2025,DIVIDEND,AAPL,0,0,0"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert len(result.transactions) == 1
        assert result.transactions[0].quantity == Decimal("0")


# ============================================================
# Integration Tests
# ============================================================

class TestRealWorldScenarios:
    """Tests mimicking real-world data patterns."""
    
    def test_typical_rsu_vest_and_sell(self):
        """Typical RSU vesting with same-day sale for taxes."""
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
03/15/2025,DEPOSIT STOCK,AAPL,RSU Vest Q1 2025,100,175.50,17550.00
03/15/2025,SALE,AAPL,Same Day Sale - Tax,40,175.50,7020.00"""
        
        result = parse_fidelity_csv(csv_content)
        
        assert len(result.vesting_events) == 1
        assert result.vesting_events[0]["value"] == Decimal("17550.00")
        
        assert len(result.sales) == 1
        assert result.sales[0]["shares"] == Decimal("40")
    
    def test_quarterly_vesting_schedule(self):
        """Quarterly RSU vesting over a year."""
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
03/15/2025,DEPOSIT STOCK,AAPL,RSU Q1,25,170.00,4250.00
06/15/2025,DEPOSIT STOCK,AAPL,RSU Q2,25,180.00,4500.00
09/15/2025,DEPOSIT STOCK,AAPL,RSU Q3,25,190.00,4750.00
12/15/2025,DEPOSIT STOCK,AAPL,RSU Q4,25,200.00,5000.00"""
        
        result = parse_fidelity_csv(csv_content)
        summary = extract_vesting_summary(result, year=2025)
        
        assert summary["vesting_count"] == 4
        assert summary["total_shares"] == Decimal("100")
        assert summary["total_value"] == Decimal("18500.00")
    
    def test_iso_exercise_and_sale(self):
        """ISO exercise followed by later sale."""
        csv_content = """Date,Action,Symbol,Description,Quantity,Price,Amount
01/15/2024,Exercise,AAPL,ISO Exercise,1000,50.00,50000.00
03/01/2025,Sale,AAPL,Sell ISO Shares,1000,180.00,180000.00"""
        
        result = parse_schwab_csv(csv_content)
        
        assert len(result.exercises) == 1
        assert result.exercises[0]["shares"] == Decimal("1000")
        
        assert len(result.sales) == 1
        assert result.sales[0]["proceeds"] == Decimal("180000.00")
