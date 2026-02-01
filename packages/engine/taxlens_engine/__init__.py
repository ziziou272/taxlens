"""
TaxLens Engine - Deterministic Tax Calculation Engine

This module provides accurate, auditable tax calculations for:
- Federal income tax (2025 rules)
- California state tax
- Equity compensation (RSU, ISO, NSO, ESPP)
- AMT calculations

IMPORTANT: All calculations use Decimal for exact arithmetic.
No floating point errors allowed in tax calculations.
"""

from taxlens_engine.federal import (
    calculate_federal_tax,
    calculate_amt,
    get_marginal_rate,
)
from taxlens_engine.models import (
    FilingStatus,
    TaxYear,
    TaxSummary,
    EquityGrant,
)
from taxlens_engine.california import (
    calculate_california_tax,
    calculate_mental_health_tax,
    calculate_sdi,
    get_ca_standard_deduction,
    get_ca_marginal_rate,
)

__version__ = "0.1.0"
__all__ = [
    "calculate_federal_tax",
    "calculate_amt",
    "get_marginal_rate",
    "FilingStatus",
    "TaxYear",
    "TaxSummary",
    "EquityGrant",
    # California
    "calculate_california_tax",
    "calculate_mental_health_tax",
    "calculate_sdi",
    "get_ca_standard_deduction",
    "get_ca_marginal_rate",
]
