"""
Extended tests for data importers (E*TRADE, Robinhood, Manual Entry).

Tests cover:
- E*TRADE CSV parsing
- Robinhood CSV parsing
- Manual entry data models
- Data validation and edge cases
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine.importers.etrade import (
    parse_etrade_csv,
    ETradeTransaction,
    ETradeParseResult,
    ETradeActionType,
    extract_vesting_summary,
    extract_sales_summary,
    _parse_date,
    _parse_decimal,
    _classify_action,
    _detect_award_type,
)
from taxlens_engine.importers.robinhood import (
    parse_robinhood_csv,
    RobinhoodTransaction,
    RobinhoodParseResult,
    RobinhoodActionType,
    calculate_cost_basis,
    calculate_gain_loss,
    extract_trading_summary,
    _extract_symbol,
)
from taxlens_engine.importers.manual_entry import (
    W2Entry,
    EquityGrantEntry,
    VestingEventEntry,
    OptionExerciseEntry,
    StockSaleEntry,
    OtherIncomeEntry,
    EstimatedPaymentEntry,
    TaxProfile,
    EquityAwardType,
    HoldingPeriod,
    IncomeType,
    create_w2_from_dict,
    create_stock_sale_from_dict,
    merge_tax_profiles,
)


# ============================================================
# E*TRADE Parser Tests
# ============================================================

class TestETradeParser:
    """Tests for E*TRADE CSV parsing."""
    
    def test_basic_csv(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Description,Quantity,Price,Amount
01/15/2025,Vest,AAPL,RSU Vesting,100,150.00,15000.00
01/15/2025,Sale,AAPL,Same Day Sale,40,150.00,6000.00"""
        
        result = parse_etrade_csv(csv_content)
        
        assert result.success
        assert len(result.transactions) == 2
        assert result.raw_rows == 2
        
        # Check vesting
        assert len(result.vesting_events) == 1
        assert result.vesting_events[0]["shares"] == Decimal("100")
        
        # Check sale
        assert len(result.sales) == 1
        assert result.sales[0]["shares"] == Decimal("40")
    
    def test_option_exercise(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Description,Quantity,Price,Amount
01/15/2025,Exercise,AAPL,ISO Exercise,500,50.00,25000.00"""
        
        result = parse_etrade_csv(csv_content)
        
        assert len(result.exercises) == 1
        assert result.exercises[0]["shares"] == Decimal("500")
        assert result.exercises[0]["award_type"] == "ISO"
    
    def test_espp_purchase(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Description,Quantity,Price,Amount
06/30/2025,ESPP Purchase,AAPL,Employee Stock Purchase Plan,50,127.50,6375.00"""
        
        result = parse_etrade_csv(csv_content)
        
        assert len(result.espp_purchases) == 1
        assert result.espp_purchases[0]["shares"] == Decimal("50")
        assert result.espp_purchases[0]["purchase_price"] == Decimal("127.50")
    
    def test_symbol_filter(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Description,Quantity,Price,Amount
01/15/2025,Vest,AAPL,RSU,100,150.00,15000.00
01/15/2025,Vest,GOOG,RSU,50,100.00,5000.00"""
        
        result = parse_etrade_csv(csv_content, symbol_filter="AAPL")
        
        assert len(result.transactions) == 1
        assert result.transactions[0].symbol == "AAPL"
    
    def test_date_parsing(self):
        assert _parse_date("01/15/2025") == date(2025, 1, 15)
        assert _parse_date("2025-01-15") == date(2025, 1, 15)
        assert _parse_date("01-15-2025") == date(2025, 1, 15)
        assert _parse_date("") is None
    
    def test_action_classification(self):
        assert _classify_action("Vest", "RSU") == ETradeActionType.VEST
        assert _classify_action("Sale") == ETradeActionType.SALE
        assert _classify_action("Exercise") == ETradeActionType.EXERCISE
        assert _classify_action("ESPP Purchase", "ESPP") == ETradeActionType.ESPP_PURCHASE
        assert _classify_action("Dividend") == ETradeActionType.DIVIDEND
    
    def test_award_type_detection(self):
        assert _detect_award_type("RSU Vesting") == "RSU"
        assert _detect_award_type("Restricted Stock Unit") == "RSU"
        assert _detect_award_type("ISO Exercise") == "ISO"
        assert _detect_award_type("Incentive Stock Option") == "ISO"
        assert _detect_award_type("NSO Exercise") == "NSO"
        assert _detect_award_type("NQSO") == "NSO"
        assert _detect_award_type("ESPP Purchase") == "ESPP"
        assert _detect_award_type("Random") is None
    
    def test_vesting_summary(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Description,Quantity,Price,Amount
03/15/2025,Vest,AAPL,RSU Q1,100,150.00,15000.00
06/15/2025,Vest,AAPL,RSU Q2,100,160.00,16000.00"""
        
        result = parse_etrade_csv(csv_content)
        summary = extract_vesting_summary(result, year=2025)
        
        assert summary["vesting_count"] == 2
        assert summary["total_shares"] == Decimal("200")
        assert summary["total_value"] == Decimal("31000.00")
    
    def test_sales_summary_with_gains(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Quantity,Price,Amount,Cost_Basis,Gain_Loss,Acquisition_Date
01/20/2025,Sale,AAPL,50,200.00,10000.00,7500.00,2500.00,01/01/2024
01/25/2025,Sale,AAPL,30,210.00,6300.00,5700.00,600.00,07/01/2024"""
        
        result = parse_etrade_csv(csv_content)
        summary = extract_sales_summary(result, year=2025)
        
        assert summary["sale_count"] == 2
        assert summary["total_shares"] == Decimal("80")
        assert summary["total_proceeds"] == Decimal("16300.00")
        assert summary["total_gain_loss"] == Decimal("3100.00")
        # First sale: held > 365 days = long term
        assert summary["long_term_gains"] == Decimal("2500.00")


# ============================================================
# Robinhood Parser Tests
# ============================================================

class TestRobinhoodParser:
    """Tests for Robinhood CSV parsing."""
    
    def test_basic_csv(self):
        csv_content = """Activity_Date,Trans_Code,Instrument,Description,Quantity,Price,Amount
01/15/2025,BUY,AAPL,Buy Market Order,10,150.00,1500.00
01/20/2025,SELL,AAPL,Sell Market Order,5,160.00,800.00"""
        
        result = parse_robinhood_csv(csv_content)
        
        assert result.success
        assert len(result.transactions) == 2
        
        # Check buy
        assert len(result.buys) == 1
        assert result.buys[0]["shares"] == Decimal("10")
        
        # Check sell
        assert len(result.sells) == 1
        assert result.sells[0]["shares"] == Decimal("5")
    
    def test_dividends(self):
        csv_content = """Activity_Date,Trans_Code,Instrument,Description,Quantity,Price,Amount
03/15/2025,DIV,AAPL,Dividend Payment,0,0,25.50
06/15/2025,CDIV,AAPL,Cash Dividend,0,0,26.00"""
        
        result = parse_robinhood_csv(csv_content)
        
        assert len(result.dividends) == 2
        total_div = sum(d["amount"] for d in result.dividends if d["amount"])
        assert total_div == Decimal("51.50")
    
    def test_dividend_reinvest(self):
        csv_content = """Activity_Date,Trans_Code,Instrument,Description,Quantity,Price,Amount
03/15/2025,DRIP,AAPL,Dividend Reinvestment,0.5,150.00,75.00"""
        
        result = parse_robinhood_csv(csv_content)
        
        # DRIP is categorized as dividend (with reinvested=True)
        assert len(result.dividends) == 1
        assert result.dividends[0]["reinvested"] is True
    
    def test_symbol_extraction(self):
        assert _extract_symbol("AAPL", "") == "AAPL"
        assert _extract_symbol("GOOGL", "Google Class A") == "GOOGL"
        # When instrument is empty, fallback to empty string
        assert _extract_symbol("", "") == ""
    
    def test_action_classification(self):
        from taxlens_engine.importers.robinhood import _classify_action
        
        assert _classify_action("BUY") == RobinhoodActionType.BUY
        assert _classify_action("SELL") == RobinhoodActionType.SELL
        assert _classify_action("DIV") == RobinhoodActionType.DIVIDEND
        assert _classify_action("DRIP", "Reinvest") == RobinhoodActionType.DIVIDEND_REINVEST
        assert _classify_action("SPLIT", "Stock Split") == RobinhoodActionType.STOCK_SPLIT
    
    def test_cost_basis_calculation(self):
        buys = [
            {"date": date(2025, 1, 15), "symbol": "AAPL", "shares": Decimal("10"), "price": Decimal("150")},
            {"date": date(2025, 2, 15), "symbol": "AAPL", "shares": Decimal("10"), "price": Decimal("160")},
        ]
        
        tax_lots = calculate_cost_basis(buys, method="fifo")
        
        assert len(tax_lots) == 2
        assert tax_lots[0]["cost_basis"] == Decimal("1500")  # 10 * 150
        assert tax_lots[1]["cost_basis"] == Decimal("1600")  # 10 * 160
    
    def test_gain_loss_calculation(self):
        buys = [
            {"date": date(2024, 1, 15), "symbol": "AAPL", "shares": Decimal("10"), "price": Decimal("150")},
        ]
        tax_lots = calculate_cost_basis(buys)
        
        sells = [
            {"date": date(2025, 6, 15), "symbol": "AAPL", "shares": Decimal("5"), "price": Decimal("200")},
        ]
        
        sales_with_basis = calculate_gain_loss(sells, tax_lots)
        
        assert len(sales_with_basis) == 1
        sale = sales_with_basis[0]
        # Proceeds: 5 * 200 = 1000, Cost: 5 * 150 = 750, Gain: 250
        assert sale["cost_basis"] == Decimal("750")
        assert sale["gain_loss"] == Decimal("250")
        assert sale["term"] == "Long"  # Held > 365 days
    
    def test_trading_summary(self):
        csv_content = """Activity_Date,Trans_Code,Instrument,Quantity,Price,Amount
01/15/2025,BUY,AAPL,10,150.00,1500.00
01/20/2025,BUY,GOOG,5,100.00,500.00
02/01/2025,SELL,AAPL,5,160.00,800.00
03/15/2025,DIV,AAPL,0,0,25.50"""
        
        result = parse_robinhood_csv(csv_content)
        summary = extract_trading_summary(result, year=2025)
        
        assert summary["total_buys"] == 2
        assert summary["total_sells"] == 1
        assert summary["total_bought_value"] == Decimal("2000.00")
        assert summary["total_sold_value"] == Decimal("800.00")
        assert summary["total_dividends"] == Decimal("25.50")
        assert set(summary["unique_symbols"]) == {"AAPL", "GOOG"}


# ============================================================
# Manual Entry Tests
# ============================================================

class TestW2Entry:
    """Tests for W2Entry model."""
    
    def test_basic_w2(self):
        w2 = W2Entry(
            employer_name="Tech Corp",
            tax_year=2025,
            wages=Decimal("200000"),
            federal_withheld=Decimal("40000"),
            social_security_wages=Decimal("176100"),
            social_security_withheld=Decimal("10918.20"),
            medicare_wages=Decimal("200000"),
            medicare_withheld=Decimal("2900"),
            state_code="CA",
            state_wages=Decimal("200000"),
            state_withheld=Decimal("18000"),
        )
        
        assert w2.wages == Decimal("200000")
        assert w2.total_withheld == Decimal("71818.20")
    
    def test_w2_with_nso_income(self):
        w2 = W2Entry(
            employer_name="Tech Corp",
            wages=Decimal("300000"),
            federal_withheld=Decimal("70000"),
            box_12_codes={"V": Decimal("100000"), "D": Decimal("23000")},
        )
        
        assert w2.nso_income == Decimal("100000")
    
    def test_create_from_dict(self):
        data = {
            "employer_name": "Test Inc",
            "wages": 150000,
            "federal_withheld": 30000,
            "state_code": "NY",
            "state_withheld": 10000,
        }
        
        w2 = create_w2_from_dict(data)
        
        assert w2.employer_name == "Test Inc"
        assert w2.wages == Decimal("150000")
        assert w2.federal_withheld == Decimal("30000")


class TestEquityGrantEntry:
    """Tests for EquityGrantEntry model."""
    
    def test_rsu_grant(self):
        grant = EquityGrantEntry(
            award_type=EquityAwardType.RSU,
            company="Tech Corp",
            symbol="TECH",
            grant_date=date(2024, 1, 15),
            shares_granted=Decimal("1000"),
            shares_vested=Decimal("250"),
            vesting_schedule="4 years monthly with 1 year cliff",
        )
        
        assert grant.shares_remaining == Decimal("750")
        assert grant.shares_exercisable == Decimal("0")  # RSU doesn't exercise
    
    def test_iso_grant(self):
        grant = EquityGrantEntry(
            award_type=EquityAwardType.ISO,
            company="Tech Corp",
            grant_date=date(2024, 1, 15),
            shares_granted=Decimal("5000"),
            shares_vested=Decimal("1250"),
            shares_exercised=Decimal("500"),
            grant_price=Decimal("50.00"),
        )
        
        assert grant.shares_exercisable == Decimal("750")


class TestVestingEventEntry:
    """Tests for VestingEventEntry model."""
    
    def test_vesting_event(self):
        vest = VestingEventEntry(
            vest_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vest=Decimal("175.50"),
            shares_withheld_for_taxes=Decimal("40"),
            federal_withheld=Decimal("3850"),
            state_withheld=Decimal("1755"),
            fica_withheld=Decimal("1341.08"),
        )
        
        assert vest.shares_net == Decimal("60")
        assert vest.gross_income == Decimal("17550.00")
        assert vest.total_withheld == Decimal("6946.08")


class TestOptionExerciseEntry:
    """Tests for OptionExerciseEntry model."""
    
    def test_nso_exercise(self):
        exercise = OptionExerciseEntry(
            exercise_date=date(2025, 6, 15),
            award_type=EquityAwardType.NSO,
            shares_exercised=Decimal("500"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("150"),
        )
        
        assert exercise.bargain_element == Decimal("100")
        assert exercise.total_bargain_element == Decimal("50000")
        assert exercise.nso_ordinary_income == Decimal("50000")
        assert exercise.iso_amt_preference == Decimal("0")
    
    def test_iso_exercise(self):
        exercise = OptionExerciseEntry(
            exercise_date=date(2025, 6, 15),
            award_type=EquityAwardType.ISO,
            shares_exercised=Decimal("500"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("150"),
            same_day_sale=False,
        )
        
        assert exercise.nso_ordinary_income == Decimal("0")
        assert exercise.iso_amt_preference == Decimal("50000")
    
    def test_iso_same_day_sale(self):
        """ISO same-day sale = no AMT preference."""
        exercise = OptionExerciseEntry(
            exercise_date=date(2025, 6, 15),
            award_type=EquityAwardType.ISO,
            shares_exercised=Decimal("500"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("150"),
            same_day_sale=True,
        )
        
        assert exercise.iso_amt_preference == Decimal("0")


class TestStockSaleEntry:
    """Tests for StockSaleEntry model."""
    
    def test_long_term_sale(self):
        sale = StockSaleEntry(
            sale_date=date(2025, 6, 15),
            symbol="AAPL",
            shares_sold=Decimal("100"),
            sale_price=Decimal("200"),
            acquisition_date=date(2024, 1, 15),
            cost_basis_per_share=Decimal("150"),
            commission=Decimal("5"),
        )
        
        assert sale.gross_proceeds == Decimal("20000")
        assert sale.net_proceeds == Decimal("19995")
        assert sale.total_cost_basis == Decimal("15000")
        assert sale.gain_loss == Decimal("4995")
        assert sale.holding_period == HoldingPeriod.LONG_TERM
        assert sale.days_held == 517
    
    def test_short_term_sale(self):
        sale = StockSaleEntry(
            sale_date=date(2025, 3, 15),
            symbol="AAPL",
            shares_sold=Decimal("50"),
            sale_price=Decimal("180"),
            acquisition_date=date(2025, 1, 15),
            cost_basis_per_share=Decimal("175"),
        )
        
        assert sale.holding_period == HoldingPeriod.SHORT_TERM
        assert sale.gain_loss == Decimal("250")
    
    def test_create_from_dict(self):
        data = {
            "sale_date": "2025-06-15",
            "symbol": "GOOG",
            "shares_sold": 10,
            "sale_price": 150,
            "acquisition_date": "2024-01-15",
            "cost_basis_per_share": 120,
        }
        
        sale = create_stock_sale_from_dict(data)
        
        assert sale.symbol == "GOOG"
        assert sale.shares_sold == Decimal("10")
        assert sale.gain_loss == Decimal("300")


class TestOtherIncomeEntry:
    """Tests for OtherIncomeEntry model."""
    
    def test_dividend_income(self):
        income = OtherIncomeEntry(
            income_type=IncomeType.DIVIDEND_QUALIFIED,
            description="AAPL Quarterly Dividend",
            amount=Decimal("500"),
            payer_name="Apple Inc",
            form_type="1099-DIV",
        )
        
        assert income.income_type == IncomeType.DIVIDEND_QUALIFIED
        assert income.amount == Decimal("500")
    
    def test_interest_income(self):
        income = OtherIncomeEntry(
            income_type=IncomeType.INTEREST,
            description="High Yield Savings",
            amount=Decimal("2500"),
            federal_withheld=Decimal("0"),
            form_type="1099-INT",
        )
        
        assert income.income_type == IncomeType.INTEREST


class TestEstimatedPaymentEntry:
    """Tests for EstimatedPaymentEntry model."""
    
    def test_estimated_payment(self):
        payment = EstimatedPaymentEntry(
            payment_date=date(2025, 4, 15),
            tax_year=2025,
            quarter=1,
            federal_amount=Decimal("5000"),
            state_amount=Decimal("2000"),
            state_code="CA",
            payment_method="EFTPS",
        )
        
        assert payment.total_amount == Decimal("7000")
        assert payment.quarter == 1


class TestTaxProfile:
    """Tests for TaxProfile model."""
    
    def test_comprehensive_profile(self):
        profile = TaxProfile(
            tax_year=2025,
            filing_status="single",
            state_of_residence="CA",
        )
        
        # Add W-2
        profile.w2_entries.append(W2Entry(
            employer_name="Tech Corp",
            wages=Decimal("200000"),
            federal_withheld=Decimal("40000"),
            state_withheld=Decimal("18000"),
        ))
        
        # Add vesting event
        profile.vesting_events.append(VestingEventEntry(
            vest_date=date(2025, 3, 15),
            shares_vested=Decimal("100"),
            fmv_at_vest=Decimal("175"),
            federal_withheld=Decimal("3850"),
            state_withheld=Decimal("1750"),
        ))
        
        # Add stock sale
        profile.stock_sales.append(StockSaleEntry(
            sale_date=date(2025, 6, 15),
            symbol="TECH",
            shares_sold=Decimal("50"),
            sale_price=Decimal("200"),
            acquisition_date=date(2024, 1, 15),
            cost_basis_per_share=Decimal("150"),
        ))
        
        # Add dividend
        profile.other_income.append(OtherIncomeEntry(
            income_type=IncomeType.DIVIDEND_QUALIFIED,
            description="Dividends",
            amount=Decimal("1000"),
        ))
        
        # Add estimated payment
        profile.estimated_payments.append(EstimatedPaymentEntry(
            payment_date=date(2025, 4, 15),
            quarter=1,
            federal_amount=Decimal("5000"),
            state_amount=Decimal("2000"),
            state_code="CA",
        ))
        
        # Check aggregations
        assert profile.total_w2_wages == Decimal("200000")
        assert profile.total_federal_withheld == Decimal("43850")
        assert profile.total_state_withheld == Decimal("19750")
        assert profile.total_long_term_gains == Decimal("2500")  # (200-150)*50
        assert profile.total_qualified_dividends == Decimal("1000")
        assert profile.total_estimated_payments_federal == Decimal("5000")
    
    def test_merge_profiles(self):
        profile1 = TaxProfile(tax_year=2025)
        profile1.w2_entries.append(W2Entry(
            employer_name="Job 1",
            wages=Decimal("100000"),
        ))
        
        profile2 = TaxProfile(tax_year=2025)
        profile2.w2_entries.append(W2Entry(
            employer_name="Job 2",
            wages=Decimal("50000"),
        ))
        profile2.other_income.append(OtherIncomeEntry(
            income_type=IncomeType.INTEREST,
            description="Interest",
            amount=Decimal("500"),
        ))
        
        merged = merge_tax_profiles([profile1, profile2])
        
        assert len(merged.w2_entries) == 2
        assert merged.total_w2_wages == Decimal("150000")
        assert len(merged.other_income) == 1
        assert merged.total_interest_income == Decimal("500")


# ============================================================
# Edge Cases
# ============================================================

class TestEdgeCases:
    """Edge cases for importers."""
    
    def test_empty_etrade_csv(self):
        csv_content = """Transaction_Date,Transaction_Type,Symbol,Quantity,Price,Amount"""
        result = parse_etrade_csv(csv_content)
        assert result.success
        assert len(result.transactions) == 0
    
    def test_empty_robinhood_csv(self):
        csv_content = """Activity_Date,Trans_Code,Instrument,Quantity,Price,Amount"""
        result = parse_robinhood_csv(csv_content)
        assert result.success
        assert len(result.transactions) == 0
    
    def test_robinhood_invalid_date(self):
        csv_content = """Activity_Date,Trans_Code,Instrument,Quantity,Price,Amount
INVALID,BUY,AAPL,10,150.00,1500.00"""
        
        result = parse_robinhood_csv(csv_content)
        assert len(result.errors) > 0
    
    def test_decimal_precision(self):
        """Ensure Decimal precision is maintained."""
        sale = StockSaleEntry(
            sale_date=date(2025, 6, 15),
            symbol="AAPL",
            shares_sold=Decimal("100.123"),
            sale_price=Decimal("175.456789"),
            acquisition_date=date(2024, 1, 15),
            cost_basis_per_share=Decimal("150.123456"),
        )
        
        # Values should maintain precision
        assert sale.gross_proceeds == Decimal("100.123") * Decimal("175.456789")
        assert sale.total_cost_basis == Decimal("100.123") * Decimal("150.123456")
    
    def test_negative_gain_loss(self):
        """Test capital loss scenario."""
        sale = StockSaleEntry(
            sale_date=date(2025, 6, 15),
            symbol="AAPL",
            shares_sold=Decimal("100"),
            sale_price=Decimal("120"),  # Sold lower than cost
            acquisition_date=date(2024, 1, 15),
            cost_basis_per_share=Decimal("150"),
        )
        
        assert sale.gain_loss == Decimal("-3000")  # Loss of $3000
    
    def test_tax_profile_with_iso_amt(self):
        """Test profile with ISO AMT calculations."""
        profile = TaxProfile()
        
        profile.option_exercises.append(OptionExerciseEntry(
            exercise_date=date(2025, 6, 15),
            award_type=EquityAwardType.ISO,
            shares_exercised=Decimal("1000"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("150"),
            same_day_sale=False,
        ))
        
        assert profile.total_iso_amt_preference == Decimal("100000")
        assert profile.total_nso_income == Decimal("0")
