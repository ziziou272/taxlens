"""
Tests for ESPP (Employee Stock Purchase Plan) calculations.
"""

import pytest
from decimal import Decimal
from datetime import date

from taxlens_engine.equity_espp import (
    ESPPPurchase,
    ESPPSale,
    ESPPTaxSummary as ESPPTaxResult,
    ESPPDispositionType as DispositionType,
    calculate_espp_sale,
    compare_espp_strategies,
    espp_qualifying_example,
    espp_disqualifying_example,
    espp_stock_dropped_example as espp_loss_example,
)


class TestESPPPurchase:
    """Tests for ESPP purchase calculations."""
    
    def test_basic_purchase(self):
        """Test basic ESPP purchase."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),  # 15% discount
            fmv_at_purchase=Decimal("120"),
            discount_rate=Decimal("0.15"),
        )
        
        assert purchase.shares_purchased == Decimal("100")
        assert purchase.purchase_price == Decimal("85")
        
    def test_total_cost(self):
        """Test total cash paid for shares."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # 100 shares × $85 = $8,500
        assert purchase.total_cost == Decimal("8500.00")
        
    def test_discount_per_share(self):
        """Test discount calculation."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # Discount = FMV at purchase - purchase price = 120 - 85 = 35
        assert purchase.discount_per_share == Decimal("35")
        
    def test_total_discount(self):
        """Test total discount received."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # Total discount = 35 × 100 = $3,500
        assert purchase.total_discount == Decimal("3500.00")
        
    def test_fmv_total(self):
        """Test total FMV at purchase."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # FMV total = 120 × 100 = $12,000
        assert purchase.fmv_total == Decimal("12000.00")


class TestESPPQualifyingDisposition:
    """Tests for qualifying disposition (favorable tax treatment)."""
    
    def test_qualifying_disposition_requirements(self):
        """Test that qualifying requires >2yr offering, >1yr purchase."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # Qualifies: >2yr from offering, >1yr from purchase
        sale = ESPPSale(
            sale_date=date(2025, 7, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("150"),
            purchase=purchase,
        )
        
        assert sale.is_qualifying_disposition is True
        assert sale.disposition_type == DispositionType.QUALIFYING
        
    def test_qualifying_ordinary_income(self):
        """Test ordinary income in qualifying disposition."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
            discount_rate=Decimal("0.15"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 7, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("150"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # Qualifying: ordinary income = lesser of actual gain or offering discount
        # Actual gain per share = 150 - 85 = 65
        # Offering discount = 100 × 0.15 = 15
        # Ordinary income = min(65, 15) × 100 = $1,500
        assert result.ordinary_income == Decimal("1500.00")
        assert result.is_long_term is True
        
    def test_qualifying_capital_gain(self):
        """Test capital gain calculation in qualifying disposition."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
            discount_rate=Decimal("0.15"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 7, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("150"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # Total gain = 150 - 85 = 65 per share × 100 = 6,500
        # Ordinary income = 1,500
        # LTCG = 6,500 - 1,500 = 5,000
        assert result.total_gain == Decimal("6500.00")
        assert result.capital_gain == Decimal("5000.00")


class TestESPPDisqualifyingDisposition:
    """Tests for disqualifying disposition."""
    
    def test_disqualifying_sold_too_early(self):
        """Test disqualifying when sold within 1 year of purchase."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 8, 15),  # Only ~46 days
            shares_sold=Decimal("100"),
            sale_price=Decimal("130"),
            purchase=purchase,
        )
        
        assert sale.is_qualifying_disposition is False
        assert sale.disposition_type == DispositionType.DISQUALIFYING
        
    def test_disqualifying_ordinary_income(self):
        """Test ordinary income = full spread at purchase for disqualifying."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 8, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("130"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # Disqualifying: ordinary income = FMV at purchase - purchase price
        # = (120 - 85) × 100 = $3,500
        assert result.ordinary_income == Decimal("3500.00")
        
    def test_disqualifying_capital_gain(self):
        """Test capital gain in disqualifying disposition."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 8, 15),
            shares_sold=Decimal("100"),
            sale_price=Decimal("130"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # Cost basis = FMV at purchase = $120
        # Capital gain = (130 - 120) × 100 = $1,000
        assert result.capital_gain == Decimal("1000.00")
        assert result.is_long_term is False  # STCG
        
    def test_disqualifying_long_term_possible(self):
        """Test that disqualifying can still be LTCG if held >1yr from purchase."""
        purchase = ESPPPurchase(
            offering_date=date(2024, 1, 1),
            purchase_date=date(2024, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # Held >1yr from purchase but <2yr from offering
        sale = ESPPSale(
            sale_date=date(2025, 8, 15),  # ~13 months from purchase
            shares_sold=Decimal("100"),
            sale_price=Decimal("130"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # Still disqualifying (not 2yr from offering)
        assert result.disposition_type == DispositionType.DISQUALIFYING
        # But capital gain is LTCG (held >1yr from purchase)
        assert result.is_long_term is True


class TestESPPLossScenarios:
    """Tests for ESPP sale at a loss."""
    
    def test_sale_at_loss_disqualifying(self):
        """Test disqualifying sale at a loss."""
        purchase = ESPPPurchase(
            offering_date=date(2024, 1, 1),
            purchase_date=date(2024, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("100"),
        )
        
        sale = ESPPSale(
            sale_date=date(2024, 9, 1),
            shares_sold=Decimal("100"),
            sale_price=Decimal("60"),  # Loss!
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # Ordinary income = spread at purchase = (100 - 85) × 100 = $1,500
        assert result.ordinary_income == Decimal("1500.00")
        
        # Capital loss = (60 - 100) × 100 = -$4,000
        assert result.capital_gain == Decimal("-4000.00")
        
    def test_sale_at_loss_qualifying(self):
        """Test qualifying sale at a loss (below purchase price)."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("100"),
            discount_rate=Decimal("0.15"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 7, 15),  # Qualifying
            shares_sold=Decimal("100"),
            sale_price=Decimal("80"),  # Below purchase price!
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        # When sold at loss, no ordinary income
        assert result.ordinary_income == Decimal("0")
        
        # All loss is capital loss
        assert result.capital_gain < Decimal("0")


class TestESPPHoldingPeriods:
    """Tests for holding period calculations."""
    
    def test_days_from_offering(self):
        """Test calculation of days from offering."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("100"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 1, 2),  # Just over 2 years
            shares_sold=Decimal("100"),
            sale_price=Decimal("100"),
            purchase=purchase,
        )
        
        assert sale.days_from_offering == 732  # >730 (leap year)
        
    def test_days_from_purchase(self):
        """Test calculation of days from purchase."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("100"),
        )
        
        sale = ESPPSale(
            sale_date=date(2024, 7, 1),  # Just over 1 year
            shares_sold=Decimal("100"),
            sale_price=Decimal("100"),
            purchase=purchase,
        )
        
        assert sale.days_from_purchase == 367  # >365
        
    def test_edge_case_exactly_2_years(self):
        """Test edge case: exactly 730 days from offering (not qualifying)."""
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("100"),
        )
        
        # Exactly 730 days = not qualifying (needs >730)
        sale = ESPPSale(
            sale_date=date(2024, 12, 31),  # 730 days from 2023-01-01
            shares_sold=Decimal("100"),
            sale_price=Decimal("100"),
            purchase=purchase,
        )
        
        assert sale.days_from_offering == 730
        assert sale.is_qualifying_disposition is False


class TestESPPExamples:
    """Test the example scenarios."""
    
    def test_qualifying_example(self):
        """Test the qualifying disposition example."""
        result = espp_qualifying_example()
        
        assert result["disposition_type"] == "qualifying"
        assert result["shares"] == Decimal("100")
        assert Decimal(str(result["ordinary_income"])) > Decimal("0")
        
    def test_disqualifying_example(self):
        """Test the disqualifying disposition example."""
        result = espp_disqualifying_example()
        
        assert result["disposition_type"] == "disqualifying"
        
    def test_loss_example(self):
        """Test the loss scenario example."""
        result = espp_loss_example()
        
        assert result["disposition_type"] == "disqualifying"
        assert Decimal(str(result["capital_gain"])) < Decimal("0")
        
    def test_comparison(self):
        """Test strategy comparison."""
        result = compare_espp_strategies()
        
        assert "immediate_sale" in result
        assert "qualifying_sale" in result
        
        # Qualifying should have less ordinary income
        assert (
            Decimal(str(result["qualifying_sale"]["ordinary_income"])) <
            Decimal(str(result["immediate_sale"]["ordinary_income"]))
        )


class TestESPPEdgeCases:
    """Edge case tests."""
    
    def test_lookback_pricing(self):
        """Test when purchase uses lower offering price (lookback)."""
        # Stock went up during offering period
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("80"),  # Lower price at offering
            purchase_price=Decimal("68"),  # 15% off the $80 offering price
            fmv_at_purchase=Decimal("120"),  # Stock is now at $120
        )
        
        # Discount from FMV = 120 - 68 = 52 per share!
        assert purchase.discount_per_share == Decimal("52")
        
    def test_fractional_shares(self):
        """Test with fractional shares."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("10.5"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("100"),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 9, 1),
            shares_sold=Decimal("10.5"),
            sale_price=Decimal("110"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        assert result.shares == Decimal("10.5")
        
    def test_partial_sale(self):
        """Test selling only some shares."""
        purchase = ESPPPurchase(
            offering_date=date(2025, 1, 1),
            purchase_date=date(2025, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
        
        # Sell only 50 shares
        sale = ESPPSale(
            sale_date=date(2025, 9, 1),
            shares_sold=Decimal("50"),
            sale_price=Decimal("130"),
            purchase=purchase,
        )
        
        result = calculate_espp_sale(sale)
        
        assert result.shares == Decimal("50")
        # Ordinary income should be for 50 shares only
        assert result.ordinary_income == Decimal("1750.00")  # (120-85) × 50
