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
    calculate_ltcg_tax,
    calculate_amt,
    calculate_fica,
    calculate_niit,
    get_marginal_rate,
)
from taxlens_engine.models import (
    FilingStatus,
    TaxYear,
    TaxSummary,
    EquityGrant,
    IncomeBreakdown,
)
from taxlens_engine.california import (
    calculate_california_tax,
    calculate_mental_health_tax,
    calculate_sdi,
    get_ca_standard_deduction,
    get_ca_marginal_rate,
)
from taxlens_engine.new_york import (
    calculate_ny_tax,
    calculate_nyc_tax,
    calculate_yonkers_surcharge,
    calculate_mctmt,
    get_ny_standard_deduction,
    get_ny_marginal_rate,
    calculate_ny_total_tax,
    calculate_ny_rsu_sourcing,
)
from taxlens_engine.washington import (
    calculate_wa_income_tax,
    calculate_wa_capital_gains_tax,
    WaCapitalGainsExemption,
)
from taxlens_engine.calculator import (
    calculate_taxes,
    format_tax_summary,
)

__version__ = "0.1.0"
__all__ = [
    # Federal
    "calculate_federal_tax",
    "calculate_ltcg_tax",
    "calculate_amt",
    "calculate_fica",
    "calculate_niit",
    "get_marginal_rate",
    # Models
    "FilingStatus",
    "TaxYear",
    "TaxSummary",
    "EquityGrant",
    "IncomeBreakdown",
    # California
    "calculate_california_tax",
    "calculate_mental_health_tax",
    "calculate_sdi",
    "get_ca_standard_deduction",
    "get_ca_marginal_rate",
    # New York
    "calculate_ny_tax",
    "calculate_nyc_tax",
    "calculate_yonkers_surcharge",
    "calculate_mctmt",
    "get_ny_standard_deduction",
    "get_ny_marginal_rate",
    "calculate_ny_total_tax",
    "calculate_ny_rsu_sourcing",
    # Washington
    "calculate_wa_income_tax",
    "calculate_wa_capital_gains_tax",
    "WaCapitalGainsExemption",
    # Calculator
    "calculate_taxes",
    "format_tax_summary",
]
