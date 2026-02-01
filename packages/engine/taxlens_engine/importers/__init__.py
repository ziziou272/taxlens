"""
Data importers for equity compensation platforms.

Supports parsing CSV exports from:
- Fidelity (NetBenefits)
- Schwab (Equity Award Center)
"""

from .fidelity import parse_fidelity_csv, FidelityTransaction
from .schwab import parse_schwab_csv, SchwabTransaction

__all__ = [
    "parse_fidelity_csv",
    "FidelityTransaction",
    "parse_schwab_csv",
    "SchwabTransaction",
]
