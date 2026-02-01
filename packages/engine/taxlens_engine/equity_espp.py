"""
ESPP (Employee Stock Purchase Plan) calculations for TaxLens.

ESPP allows employees to purchase company stock at a discount.
Typical plan: 15% discount from lower of:
- Price at offering start, or
- Price at purchase date

Tax treatment depends on holding period:

Qualifying Disposition:
- Hold > 2 years from offering date AND > 1 year from purchase
- Ordinary income = lesser of:
  (1) Actual gain, or
  (2) Discount from offering date price (typically 15%)
- Remainder is long-term capital gain

Disqualifying Disposition:
- Fails holding requirements
- Ordinary income = Actual discount received at purchase
- Remainder is capital gain (short or long term based on holding)
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from enum import Enum
from typing import Optional


class ESPPDispositionType(str, Enum):
    """Type of ESPP disposition."""
    QUALIFYING = "qualifying"
    DISQUALIFYING = "disqualifying"


@dataclass
class ESPPPurchase:
    """
    Represents an ESPP purchase.
    
    Accepts direct purchase_price and fmv_at_purchase (per share) for flexibility.
    """
    offering_date: date
    purchase_date: date
    shares_purchased: Decimal
    offering_price: Decimal  # FMV at offering start
    purchase_price: Decimal  # Actual price paid per share
    fmv_at_purchase: Decimal  # FMV per share at purchase
    discount_rate: Decimal = Decimal("0.15")  # Typically 15%
    
    @property
    def lookback_price(self) -> Decimal:
        """Lower of offering price or purchase FMV."""
        return min(self.offering_price, self.fmv_at_purchase)
    
    @property
    def total_cost(self) -> Decimal:
        """Total cash paid for shares."""
        return (self.shares_purchased * self.purchase_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def fmv_total(self) -> Decimal:
        """Total FMV at purchase."""
        return (self.shares_purchased * self.fmv_at_purchase).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def discount_per_share(self) -> Decimal:
        """Discount per share = FMV - purchase price."""
        return self.fmv_at_purchase - self.purchase_price
    
    @property
    def total_discount(self) -> Decimal:
        """Total discount received."""
        return (self.discount_per_share * self.shares_purchased).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def discount_received(self) -> Decimal:
        """
        Actual discount = FMV at purchase - price paid.
        
        This is the taxable spread for disqualifying disposition.
        """
        spread = self.fmv_at_purchase - self.purchase_price
        return (spread * self.shares_purchased).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def statutory_discount(self) -> Decimal:
        """
        Statutory discount = 15% of offering date price.
        
        For qualifying disposition, ordinary income is capped at this amount.
        """
        discount_per_share = self.offering_price * self.discount_rate
        return (discount_per_share * self.shares_purchased).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


@dataclass
class ESPPSale:
    """
    Represents selling ESPP shares.
    """
    sale_date: date
    shares_sold: Decimal
    sale_price: Decimal
    purchase: ESPPPurchase
    
    @property
    def proceeds(self) -> Decimal:
        """Sale proceeds."""
        return (self.shares_sold * self.sale_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @property
    def days_from_offering(self) -> int:
        """Days held from offering date."""
        return (self.sale_date - self.purchase.offering_date).days
    
    @property
    def days_from_purchase(self) -> int:
        """Days held from purchase date."""
        return (self.sale_date - self.purchase.purchase_date).days
    
    @property
    def disposition_type(self) -> ESPPDispositionType:
        """
        Determine disposition type.
        
        Qualifying requires:
        - > 2 years from offering date
        - > 1 year from purchase date
        """
        if self.days_from_offering > 730 and self.days_from_purchase > 365:
            return ESPPDispositionType.QUALIFYING
        return ESPPDispositionType.DISQUALIFYING
    
    @property
    def is_qualifying(self) -> bool:
        """Is this a qualifying disposition?"""
        return self.disposition_type == ESPPDispositionType.QUALIFYING
    
    @property
    def is_qualifying_disposition(self) -> bool:
        """Alias for is_qualifying."""
        return self.is_qualifying
    
    @property
    def total_gain(self) -> Decimal:
        """Total economic gain (sale - purchase price)."""
        cost = self.shares_sold * self.purchase.purchase_price
        gain = self.proceeds - cost
        return gain.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property
    def ordinary_income(self) -> Decimal:
        """
        Ordinary income portion.
        
        Qualifying: Lesser of actual gain or statutory discount (0 if loss)
        Disqualifying: Actual discount received at purchase (FMV - purchase price)
        """
        if self.is_qualifying:
            # Cap at statutory discount (15% of offering price)
            statutory = self.purchase.statutory_discount * (
                self.shares_sold / self.purchase.shares_purchased
            )
            # Also cap at actual gain (if stock went down)
            if self.total_gain <= 0:
                return Decimal("0")
            return min(self.total_gain, statutory).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            # Disqualifying: ordinary income = (FMV at purchase - purchase price) × shares
            # This is the "bargain element" - always taxable as W-2 income
            discount_per_share = self.purchase.fmv_at_purchase - self.purchase.purchase_price
            if discount_per_share <= 0:
                return Decimal("0")
            return (discount_per_share * self.shares_sold).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
    
    @property
    def capital_gain(self) -> Decimal:
        """
        Capital gain portion.
        
        Qualifying: Total gain - ordinary income (based on purchase price cost basis)
        Disqualifying: (Sale price - FMV at purchase) × shares (FMV is cost basis)
        """
        if self.is_qualifying:
            return (self.total_gain - self.ordinary_income).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            # Disqualifying: cost basis = FMV at purchase
            gain_per_share = self.sale_price - self.purchase.fmv_at_purchase
            return (gain_per_share * self.shares_sold).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
    
    @property
    def is_long_term_capital_gain(self) -> bool:
        """Is capital gain long-term?"""
        # Qualifying is always long-term by definition
        if self.is_qualifying:
            return True
        # Disqualifying: based on holding from purchase
        return self.days_from_purchase >= 365


@dataclass
class ESPPTaxSummary:
    """Summary of ESPP tax implications."""
    disposition_type: ESPPDispositionType
    
    # Purchase details
    shares: Decimal
    offering_price: Decimal
    purchase_price: Decimal
    fmv_at_purchase: Decimal  # Renamed from purchase_date_fmv
    
    # Sale details
    sale_price: Decimal
    proceeds: Decimal
    
    # Tax treatment
    ordinary_income: Decimal
    capital_gain: Decimal
    is_long_term: bool
    total_gain: Decimal


def calculate_espp_purchase(
    shares: Decimal,
    offering_price: Decimal,
    purchase_date_fmv: Decimal,
    offering_date: date,
    purchase_date: date,
    discount_rate: Decimal = Decimal("0.15"),
) -> ESPPPurchase:
    """
    Calculate ESPP purchase details.
    
    Args:
        shares: Shares purchased
        offering_price: FMV at offering start
        purchase_date_fmv: FMV at purchase
        offering_date: Offering period start
        purchase_date: Purchase date
        discount_rate: Discount (typically 15%)
        
    Returns:
        ESPPPurchase with calculated values
    """
    # Calculate purchase price using lookback and discount
    lookback_price = min(offering_price, purchase_date_fmv)
    purchase_price = (lookback_price * (1 - discount_rate)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    return ESPPPurchase(
        offering_date=offering_date,
        purchase_date=purchase_date,
        shares_purchased=shares,
        offering_price=offering_price,
        purchase_price=purchase_price,
        fmv_at_purchase=purchase_date_fmv,
        discount_rate=discount_rate,
    )


def analyze_espp_sale(
    purchase: ESPPPurchase,
    sale_price: Decimal,
    sale_date: date,
    shares_sold: Optional[Decimal] = None,
) -> ESPPTaxSummary:
    """
    Analyze ESPP sale for tax implications.
    
    Args:
        purchase: Original ESPP purchase
        sale_price: Sale price per share
        sale_date: Date of sale
        shares_sold: Shares to sell (defaults to all)
        
    Returns:
        ESPPTaxSummary with complete analysis
    """
    if shares_sold is None:
        shares_sold = purchase.shares_purchased
    
    sale = ESPPSale(
        sale_date=sale_date,
        shares_sold=shares_sold,
        sale_price=sale_price,
        purchase=purchase,
    )
    
    return ESPPTaxSummary(
        disposition_type=sale.disposition_type,
        shares=shares_sold,
        offering_price=purchase.offering_price,
        purchase_price=purchase.purchase_price,
        fmv_at_purchase=purchase.fmv_at_purchase,
        sale_price=sale_price,
        proceeds=sale.proceeds,
        ordinary_income=sale.ordinary_income,
        capital_gain=sale.capital_gain,
        is_long_term=sale.is_long_term_capital_gain,
        total_gain=sale.total_gain,
    )


def calculate_espp_sale(sale: ESPPSale) -> ESPPTaxSummary:
    """
    Calculate ESPP sale tax implications from an ESPPSale object.
    
    Compatibility wrapper for analyze_espp_sale.
    
    Args:
        sale: ESPPSale object with all sale details
        
    Returns:
        ESPPTaxSummary with complete analysis
    """
    return analyze_espp_sale(
        purchase=sale.purchase,
        sale_price=sale.sale_price,
        sale_date=sale.sale_date,
        shares_sold=sale.shares_sold,
    )


def compare_espp_strategies(
    purchase: Optional[ESPPPurchase] = None,
    current_price: Optional[Decimal] = None,
    years_held: int = 3,
) -> dict:
    """
    Compare different ESPP sale strategies.
    
    Args:
        purchase: Original ESPP purchase (uses example if not provided)
        current_price: Current stock price (uses example if not provided)
        years_held: Years to project
        
    Returns:
        Comparison of qualifying vs disqualifying disposition
    """
    from datetime import timedelta
    
    # Use example values if not provided
    if purchase is None:
        purchase = ESPPPurchase(
            offering_date=date(2023, 1, 1),
            purchase_date=date(2023, 6, 30),
            shares_purchased=Decimal("100"),
            offering_price=Decimal("100"),
            purchase_price=Decimal("85"),
            fmv_at_purchase=Decimal("120"),
        )
    if current_price is None:
        current_price = Decimal("150")
    
    # Immediate/disqualifying sale (now)
    disq_sale_date = purchase.purchase_date + timedelta(days=180)  # 6 months
    disq = analyze_espp_sale(
        purchase=purchase,
        sale_price=current_price,
        sale_date=disq_sale_date,
    )
    
    # Qualifying sale (after holding period)
    qual_sale_date = max(
        purchase.offering_date + timedelta(days=731),  # >2yr from offering
        purchase.purchase_date + timedelta(days=366),   # >1yr from purchase
    )
    qual = analyze_espp_sale(
        purchase=purchase,
        sale_price=current_price,
        sale_date=qual_sale_date,
    )
    
    return {
        "immediate_sale": {
            "ordinary_income": disq.ordinary_income,
            "capital_gain": disq.capital_gain,
            "is_long_term": disq.is_long_term,
            "total_gain": disq.total_gain,
        },
        "qualifying_sale": {
            "ordinary_income": qual.ordinary_income,
            "capital_gain": qual.capital_gain,
            "is_long_term": qual.is_long_term,
            "total_gain": qual.total_gain,
        },
        "tax_savings_potential": disq.ordinary_income - qual.ordinary_income,
    }


# ============================================================
# ESPP Examples
# ============================================================

def espp_qualifying_example() -> dict:
    """
    Example: ESPP qualifying disposition.
    
    Scenario:
    - Offering price: $100
    - Purchase price: $85 (15% discount on $100 lookback)
    - Sale: $150 after holding requirements met
    """
    purchase = calculate_espp_purchase(
        shares=Decimal("100"),
        offering_price=Decimal("100"),
        purchase_date_fmv=Decimal("120"),  # Stock went up during offering
        offering_date=date(2022, 7, 1),
        purchase_date=date(2022, 12, 31),
    )
    
    summary = analyze_espp_sale(
        purchase=purchase,
        sale_price=Decimal("150"),
        sale_date=date(2025, 1, 15),  # > 2 yrs from offering, > 1 yr from purchase
    )
    
    return {
        "scenario": "ESPP Qualifying Disposition",
        "shares": summary.shares,
        "offering_price": summary.offering_price,
        "fmv_at_purchase": summary.fmv_at_purchase,
        "purchase_price": summary.purchase_price,  # 85% of $100 = $85
        "sale_price": summary.sale_price,
        "disposition_type": summary.disposition_type.value,
        "total_gain": summary.total_gain,  # (150-85) * 100 = $6,500
        "ordinary_income": summary.ordinary_income,  # Capped at 15% of $100
        "capital_gain": summary.capital_gain,
        "is_long_term": summary.is_long_term,
        "notes": [
            "Lookback: Used $100 offering price (lower than $120)",
            "Purchase price: $85 (15% discount on $100)",
            f"Ordinary income capped at statutory discount: ${summary.ordinary_income:,.2f}",
            f"Remainder is LTCG: ${summary.capital_gain:,.2f}",
        ],
    }


def espp_disqualifying_example() -> dict:
    """
    Example: ESPP disqualifying disposition.
    
    Scenario:
    - Offering price: $100
    - Stock went up to $120 at purchase
    - Sold early at $130
    """
    purchase = calculate_espp_purchase(
        shares=Decimal("100"),
        offering_price=Decimal("100"),
        purchase_date_fmv=Decimal("120"),
        offering_date=date(2024, 7, 1),
        purchase_date=date(2024, 12, 31),
    )
    
    summary = analyze_espp_sale(
        purchase=purchase,
        sale_price=Decimal("130"),
        sale_date=date(2025, 6, 1),  # < 1 year from purchase
    )
    
    return {
        "scenario": "ESPP Disqualifying Disposition",
        "shares": summary.shares,
        "offering_price": summary.offering_price,
        "fmv_at_purchase": summary.fmv_at_purchase,
        "purchase_price": summary.purchase_price,
        "sale_price": summary.sale_price,
        "disposition_type": summary.disposition_type.value,
        "total_gain": summary.total_gain,
        "ordinary_income": summary.ordinary_income,  # Full discount: 120-85 = $35/share
        "capital_gain": summary.capital_gain,
        "is_long_term": summary.is_long_term,
        "notes": [
            "Disqualifying: sold before holding periods met",
            f"Ordinary income = actual discount: ${summary.ordinary_income:,.2f}",
            f"Capital gain: ${summary.capital_gain:,.2f}",
            "Capital gain is short-term (< 1 year from purchase)",
        ],
    }


def espp_stock_dropped_example() -> dict:
    """
    Example: ESPP when stock dropped below purchase price.
    
    Scenario:
    - Purchased at $85
    - Stock dropped to $70
    """
    purchase = calculate_espp_purchase(
        shares=Decimal("100"),
        offering_price=Decimal("100"),
        purchase_date_fmv=Decimal("100"),
        offering_date=date(2024, 1, 1),
        purchase_date=date(2024, 6, 30),
    )
    
    summary = analyze_espp_sale(
        purchase=purchase,
        sale_price=Decimal("70"),
        sale_date=date(2024, 12, 1),
    )
    
    return {
        "scenario": "ESPP Stock Dropped",
        "shares": summary.shares,
        "purchase_price": summary.purchase_price,
        "sale_price": summary.sale_price,
        "disposition_type": summary.disposition_type.value,
        "total_gain": summary.total_gain,  # Negative (loss)
        "ordinary_income": summary.ordinary_income,  # $0 (no gain)
        "capital_gain": summary.capital_gain,  # Full loss
        "notes": [
            f"Purchased at ${summary.purchase_price}, sold at $70",
            "No ordinary income (sold at a loss)",
            f"Capital loss: ${summary.capital_gain:,.2f}",
            "Can offset other capital gains",
        ],
    }
