"""
Red Flag Alert System for TaxLens.

Proactive alerts for:
- Underwithholding penalties
- AMT triggers from ISO exercises
- Washington State capital gains tax
- Other tax planning concerns
"""

from .underwithholding import (
    check_underwithholding,
    UnderwithholdingAlert,
    SafeHarborStatus,
)
from .amt_warning import (
    check_amt_trigger,
    AMTAlert,
    estimate_amt_liability,
)
from .capital_gains import (
    check_wa_capital_gains,
    WACapitalGainsAlert,
)

__all__ = [
    # Underwithholding
    "check_underwithholding",
    "UnderwithholdingAlert",
    "SafeHarborStatus",
    # AMT
    "check_amt_trigger",
    "AMTAlert",
    "estimate_amt_liability",
    # WA Capital Gains
    "check_wa_capital_gains",
    "WACapitalGainsAlert",
]
