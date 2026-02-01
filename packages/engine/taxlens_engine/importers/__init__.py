"""
Data importers for equity compensation platforms.

Supports parsing CSV exports from:
- Fidelity (NetBenefits)
- Schwab (Equity Award Center)
- E*TRADE
- Robinhood

Also provides manual entry data models.
"""

from .fidelity import parse_fidelity_csv, FidelityTransaction, FidelityParseResult
from .schwab import parse_schwab_csv, SchwabTransaction, SchwabParseResult
from .etrade import parse_etrade_csv, ETradeTransaction, ETradeParseResult
from .robinhood import parse_robinhood_csv, RobinhoodTransaction, RobinhoodParseResult
from .manual_entry import (
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
)

__all__ = [
    # Fidelity
    "parse_fidelity_csv",
    "FidelityTransaction",
    "FidelityParseResult",
    # Schwab
    "parse_schwab_csv",
    "SchwabTransaction",
    "SchwabParseResult",
    # E*TRADE
    "parse_etrade_csv",
    "ETradeTransaction",
    "ETradeParseResult",
    # Robinhood
    "parse_robinhood_csv",
    "RobinhoodTransaction",
    "RobinhoodParseResult",
    # Manual Entry
    "W2Entry",
    "EquityGrantEntry",
    "VestingEventEntry",
    "OptionExerciseEntry",
    "StockSaleEntry",
    "OtherIncomeEntry",
    "EstimatedPaymentEntry",
    "TaxProfile",
    "EquityAwardType",
    "HoldingPeriod",
    "IncomeType",
]
