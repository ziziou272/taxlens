"""
Tests for NSO and ESPP calculations.

NSO (Non-Qualified Stock Options):
- Ordinary income at exercise
- Capital gain on subsequent sale

ESPP (Employee Stock Purchase Plan):
- Qualifying vs disqualifying dispositions
- Ordinary income calculation
- Lookback provision
"""

from decimal import Decimal
from datetime import date
import pytest

from taxlens_engine.equity_nso import (
    NSOExercise,
    NSOSale,
    calculate_nso_exercise,
    estimate_nso_withholding,
    nso_exercise_and_hold_example,
    nso_cashless_exercise_example,
)
from taxlens_engine.equity_espp import (
    ESPPPurchase,
    ESPPSale,
    ESPPDispositionType,
    calculate_espp_purchase,
    analyze_espp_sale,
    espp_qualifying_example,
    espp_disqualifying_example,
    espp_stock_dropped_example,
)


# ============================================================
# NSO Tests
# ============================================================

class TestNSOExercise:
    """Test NSO exercise calculations."""
    
    def test_basic_exercise(self):
        """Basic NSO exercise creates ordinary income."""
        exercise = calculate_nso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("10"),
            fmv_at_exercise=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        # Spread = $50 - $10 = $40/share
        assert exercise.spread == Decimal("40")
        
        # Ordinary income = $40 × 1000 = $40,000
        assert exercise.ordinary_income == Decimal("40000.00")
        
        # Cost basis = FMV = $50
        assert exercise.cost_basis_per_share == Decimal("50")
        
        # Cash needed = $10 × 1000 = $10,000
        assert exercise.total_cost == Decimal("10000.00")
    
    def test_underwater_exercise(self):
        """Exercise when underwater (FMV < strike)."""
        exercise = calculate_nso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("30"),
            exercise_date=date(2025, 6, 1),
        )
        
        # No spread when underwater
        assert exercise.spread == Decimal("0")
        assert exercise.ordinary_income == Decimal("0.00")
    
    def test_at_the_money_exercise(self):
        """Exercise at exactly strike price."""
        exercise = calculate_nso_exercise(
            shares=Decimal("1000"),
            strike_price=Decimal("50"),
            fmv_at_exercise=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        assert exercise.spread == Decimal("0")
        assert exercise.ordinary_income == Decimal("0.00")


class TestNSOSale:
    """Test NSO sale calculations."""
    
    def test_sale_with_gain(self):
        """Sale with additional capital gain."""
        sale = NSOSale(
            sale_date=date(2026, 6, 1),
            shares_sold=Decimal("1000"),
            sale_price=Decimal("70"),
            cost_basis_per_share=Decimal("50"),  # FMV at exercise
            exercise_date=date(2025, 6, 1),
        )
        
        # Capital gain = (70 - 50) × 1000 = $20,000
        assert sale.capital_gain == Decimal("20000.00")
        assert sale.is_long_term is True  # > 1 year
    
    def test_sale_with_loss(self):
        """Sale with capital loss."""
        sale = NSOSale(
            sale_date=date(2025, 12, 1),
            shares_sold=Decimal("1000"),
            sale_price=Decimal("40"),
            cost_basis_per_share=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        # Capital loss = (40 - 50) × 1000 = -$10,000
        assert sale.capital_gain == Decimal("-10000.00")
        assert sale.is_long_term is False  # < 1 year
    
    def test_immediate_sale(self):
        """Immediate sale (cashless exercise)."""
        sale = NSOSale(
            sale_date=date(2025, 6, 1),
            shares_sold=Decimal("1000"),
            sale_price=Decimal("50"),  # Same as FMV
            cost_basis_per_share=Decimal("50"),
            exercise_date=date(2025, 6, 1),
        )
        
        # No capital gain
        assert sale.capital_gain == Decimal("0.00")


class TestNSOWithholding:
    """Test NSO withholding estimation."""
    
    def test_standard_withholding(self):
        """Test withholding with standard rates."""
        withholding = estimate_nso_withholding(Decimal("40000"))
        
        # Federal: 22% of $40,000 = $8,800
        assert withholding["federal"] == Decimal("8800.00")
        
        # State (CA): 10.23% = $4,092
        assert withholding["state"] == Decimal("4092.00")
        
        # SS: 6.2% = $2,480
        assert withholding["social_security"] == Decimal("2480.00")
        
        # Medicare: 1.45% = $580
        assert withholding["medicare"] == Decimal("580.00")
    
    def test_over_ss_limit(self):
        """Test withholding when over SS limit."""
        withholding = estimate_nso_withholding(
            ordinary_income=Decimal("100000"),
            over_ss_limit=True,
        )
        
        # No SS tax
        assert withholding["social_security"] == Decimal("0.00")
        # Medicare still applies
        assert withholding["medicare"] == Decimal("1450.00")


class TestNSOExamples:
    """Test NSO example scenarios."""
    
    def test_exercise_and_hold(self):
        """Test exercise and hold example."""
        result = nso_exercise_and_hold_example()
        
        assert result["ordinary_income"] == Decimal("40000.00")
        assert result["cost_basis"] == Decimal("50")
        assert "withholding" in result
    
    def test_cashless_exercise(self):
        """Test cashless exercise example."""
        result = nso_cashless_exercise_example()
        
        assert result["ordinary_income"] == Decimal("40000.00")
        assert result["capital_gain"] == Decimal("0.00")


# ============================================================
# ESPP Tests
# ============================================================

class TestESPPPurchase:
    """Test ESPP purchase calculations."""
    
    def test_lookback_lower_offering(self):
        """Lookback uses offering price when it's lower."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_date_fmv=Decimal("150"),  # Stock went up
            offering_date=date(2024, 1, 1),
            purchase_date=date(2024, 6, 30),
        )
        
        # Lookback = $100 (lower)
        assert purchase.lookback_price == Decimal("100")
        # Purchase price = 85% of $100 = $85
        assert purchase.purchase_price == Decimal("85.00")
    
    def test_lookback_lower_purchase(self):
        """Lookback uses purchase FMV when it's lower."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("150"),
            purchase_date_fmv=Decimal("100"),  # Stock went down
            offering_date=date(2024, 1, 1),
            purchase_date=date(2024, 6, 30),
        )
        
        # Lookback = $100 (lower)
        assert purchase.lookback_price == Decimal("100")
        # Purchase price = 85% of $100 = $85
        assert purchase.purchase_price == Decimal("85.00")
    
    def test_discount_received(self):
        """Test actual discount calculation."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_date_fmv=Decimal("120"),
            offering_date=date(2024, 1, 1),
            purchase_date=date(2024, 6, 30),
        )
        
        # Purchase at $85, FMV is $120
        # Discount = (120 - 85) × 100 = $3,500
        assert purchase.discount_received == Decimal("3500.00")
    
    def test_statutory_discount(self):
        """Test statutory discount (for qualifying)."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_date_fmv=Decimal("120"),
            offering_date=date(2024, 1, 1),
            purchase_date=date(2024, 6, 30),
        )
        
        # Statutory = 15% of offering price × shares
        # = 0.15 × $100 × 100 = $1,500
        assert purchase.statutory_discount == Decimal("1500.00")


class TestESPPDisposition:
    """Test ESPP disposition type determination."""
    
    def test_qualifying_disposition(self):
        """Sale meets both holding requirements."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_date_fmv=Decimal("100"),
            offering_date=date(2022, 1, 1),
            purchase_date=date(2022, 6, 30),
        )
        
        sale = ESPPSale(
            sale_date=date(2024, 2, 1),  # > 2 yrs from offering, > 1 yr from purchase
            shares_sold=Decimal("100"),
            sale_price=Decimal("150"),
            purchase=purchase,
        )
        
        assert sale.disposition_type == ESPPDispositionType.QUALIFYING
    
    def test_disqualifying_short_from_offering(self):
        """Disqualifying: < 2 years from offering."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_date_fmv=Decimal("100"),
            offering_date=date(2023, 7, 1),
            purchase_date=date(2023, 12, 31),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 6, 1),  # > 1 yr from purchase but < 2 yrs from offering
            shares_sold=Decimal("100"),
            sale_price=Decimal("150"),
            purchase=purchase,
        )
        
        assert sale.disposition_type == ESPPDispositionType.DISQUALIFYING
    
    def test_disqualifying_short_from_purchase(self):
        """Disqualifying: < 1 year from purchase."""
        purchase = calculate_espp_purchase(
            shares=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_date_fmv=Decimal("100"),
            offering_date=date(2022, 1, 1),
            purchase_date=date(2024, 6, 30),
        )
        
        sale = ESPPSale(
            sale_date=date(2025, 1, 1),  # > 2 yrs from offering but < 1 yr from purchase
            shares_sold=Decimal("100"),
            sale_price=Decimal("150"),
            purchase=purchase,
        )
        
        assert sale.disposition_type == ESPPDispositionType.DISQUALIFYING


class TestESPPTaxTreatment:
    """Test ESPP tax treatment."""
    
    def test_qualifying_ordinary_income_capped(self):
        """Qualifying: ordinary income capped at statutory discount."""
        summary = analyze_espp_sale(
            purchase=calculate_espp_purchase(
                shares=Decimal("100"),
                offering_price=Decimal("100"),
                purchase_date_fmv=Decimal("120"),  # Actual discount is $35/share
                offering_date=date(2022, 1, 1),
                purchase_date=date(2022, 6, 30),
            ),
            sale_price=Decimal("150"),
            sale_date=date(2024, 7, 1),  # Qualifying
        )
        
        # Total gain = (150 - 85) × 100 = $6,500
        assert summary.total_gain == Decimal("6500.00")
        
        # Ordinary income capped at 15% of offering = $1,500
        assert summary.ordinary_income == Decimal("1500.00")
        
        # Capital gain = $6,500 - $1,500 = $5,000
        assert summary.capital_gain == Decimal("5000.00")
        assert summary.is_long_term is True
    
    def test_disqualifying_ordinary_income_full_discount(self):
        """Disqualifying: ordinary income = actual discount."""
        summary = analyze_espp_sale(
            purchase=calculate_espp_purchase(
                shares=Decimal("100"),
                offering_price=Decimal("100"),
                purchase_date_fmv=Decimal("120"),
                offering_date=date(2024, 1, 1),
                purchase_date=date(2024, 6, 30),
            ),
            sale_price=Decimal("130"),
            sale_date=date(2024, 12, 1),  # Disqualifying
        )
        
        # Total gain = (130 - 85) × 100 = $4,500
        assert summary.total_gain == Decimal("4500.00")
        
        # Ordinary income = actual discount = (120 - 85) × 100 = $3,500
        assert summary.ordinary_income == Decimal("3500.00")
        
        # Capital gain = $4,500 - $3,500 = $1,000
        assert summary.capital_gain == Decimal("1000.00")
    
    def test_qualifying_loss(self):
        """Qualifying disposition at a loss."""
        summary = analyze_espp_sale(
            purchase=calculate_espp_purchase(
                shares=Decimal("100"),
                offering_price=Decimal("100"),
                purchase_date_fmv=Decimal("100"),
                offering_date=date(2022, 1, 1),
                purchase_date=date(2022, 6, 30),
            ),
            sale_price=Decimal("70"),
            sale_date=date(2024, 7, 1),  # Qualifying
        )
        
        # Total loss = (70 - 85) × 100 = -$1,500
        assert summary.total_gain == Decimal("-1500.00")
        
        # No ordinary income when sold at loss
        assert summary.ordinary_income == Decimal("0")
        
        # Full loss is capital loss
        assert summary.capital_gain == Decimal("-1500.00")


class TestESPPExamples:
    """Test ESPP example scenarios."""
    
    def test_qualifying_example(self):
        """Test qualifying disposition example."""
        result = espp_qualifying_example()
        
        assert result["disposition_type"] == "qualifying"
        assert result["is_long_term"] is True
        # Ordinary income should be capped
        assert result["ordinary_income"] == Decimal("1500.00")
    
    def test_disqualifying_example(self):
        """Test disqualifying disposition example."""
        result = espp_disqualifying_example()
        
        assert result["disposition_type"] == "disqualifying"
        # Ordinary income is full discount
        assert result["ordinary_income"] == Decimal("3500.00")
    
    def test_stock_dropped_example(self):
        """Test stock dropped example."""
        result = espp_stock_dropped_example()
        
        # Disqualifying disposition: ordinary income = discount at purchase
        # = (FMV at purchase - purchase price) × shares = (100 - 85) × 100 = 1500
        assert result["ordinary_income"] == Decimal("1500.00")
        # Capital loss = (sale price - FMV at purchase) × shares
        # = (70 - 100) × 100 = -3000
        assert result["capital_gain"] < Decimal("0")
