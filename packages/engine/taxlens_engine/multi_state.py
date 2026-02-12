"""
Multi-state income sourcing and tax calculations for TaxLens.

Handles:
- 183-day residency rule
- Work-day allocation for income sourcing
- Part-year move detection (e.g., CA→WA mid-year)
- RSU/equity income allocation between grant and vest states
- Remote work tracking
- Tax calculation across CA, NY, WA

Based on 2025 tax rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from taxlens_engine.models import FilingStatus
from taxlens_engine.california import calculate_california_tax, calculate_sdi
from taxlens_engine.new_york import (
    calculate_ny_tax,
    calculate_nyc_tax,
)
from taxlens_engine.washington import calculate_wa_capital_gains_tax


RESIDENCY_THRESHOLD = 183  # Days to establish tax residency


@dataclass
class StatePresence:
    """Track days present and working in a state."""

    state: str  # Two-letter code, e.g. "CA", "NY", "WA"
    days: int = 0  # Calendar days present
    work_days: int = 0  # Days actually worked in the state


@dataclass
class MultiStateCalculator:
    """Calculate multi-state tax obligations.

    Parameters
    ----------
    presences : list[StatePresence]
        Days in each state for the tax year.
    move_date : date | None
        Date of a mid-year relocation (if any).
    filing_status : FilingStatus
        Federal/state filing status.
    is_nyc_resident : bool
        Whether the taxpayer is a NYC resident (for city tax).
    """

    presences: list[StatePresence]
    move_date: Optional[date] = None
    filing_status: FilingStatus = FilingStatus.SINGLE
    is_nyc_resident: bool = False

    # ------------------------------------------------------------------ #
    # Residency
    # ------------------------------------------------------------------ #

    def determine_residency(self) -> list[str]:
        """Return state codes where the taxpayer is a tax resident (183+ days)."""
        return [p.state for p in self.presences if p.days >= RESIDENCY_THRESHOLD]

    # ------------------------------------------------------------------ #
    # Part-year move detection
    # ------------------------------------------------------------------ #

    def detect_part_year_move(self) -> Optional[tuple[str, str, date]]:
        """Detect a mid-year relocation.

        Returns (from_state, to_state, move_date) or None.
        Heuristic: if ``move_date`` is set, the two states with the most days
        are treated as "from" and "to" based on which has more early-year days.
        """
        if self.move_date is None:
            return None
        if len(self.presences) < 2:
            return None

        sorted_p = sorted(self.presences, key=lambda p: p.days, reverse=True)
        from_state = sorted_p[0].state
        to_state = sorted_p[1].state
        return (from_state, to_state, self.move_date)

    # ------------------------------------------------------------------ #
    # Income allocation
    # ------------------------------------------------------------------ #

    def _total_work_days(self) -> int:
        return sum(p.work_days for p in self.presences)

    def allocate_income(
        self,
        total_income: Decimal,
        income_type: str = "wage",
    ) -> dict[str, Decimal]:
        """Allocate income across states by work-day proportion.

        ``income_type`` can be ``"wage"`` (work-day allocation) or
        ``"capital_gain"`` (allocated to state of residence).
        """
        total_wd = self._total_work_days()
        if total_wd == 0:
            # Fall back to calendar-day allocation
            total_days = sum(p.days for p in self.presences) or 1
            return {
                p.state: (total_income * Decimal(p.days) / Decimal(total_days)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                for p in self.presences
            }

        if income_type == "capital_gain":
            # Capital gains attributed to domicile state(s)
            residents = self.determine_residency()
            if residents:
                per_state = (total_income / Decimal(len(residents))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                return {s: per_state for s in residents}
            # Fallback: largest-presence state
            top = max(self.presences, key=lambda p: p.days)
            return {top.state: total_income}

        # Wage / ordinary income → work-day allocation
        alloc: dict[str, Decimal] = {}
        for p in self.presences:
            ratio = Decimal(p.work_days) / Decimal(total_wd)
            alloc[p.state] = (total_income * ratio).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return alloc

    def allocate_equity_income(
        self,
        equity_income: Decimal,
        grant_date: date,
        vest_date: date,
        work_days_by_state: dict[str, int],
    ) -> dict[str, Decimal]:
        """Allocate RSU/equity income using the grant-to-vest work-day rule.

        ``work_days_by_state`` maps state → work days in that state between
        ``grant_date`` and ``vest_date``.
        """
        total_wd = sum(work_days_by_state.values())
        if total_wd == 0:
            return {}
        alloc: dict[str, Decimal] = {}
        for state, wd in work_days_by_state.items():
            ratio = Decimal(wd) / Decimal(total_wd)
            alloc[state] = (equity_income * ratio).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return alloc

    # ------------------------------------------------------------------ #
    # Tax calculations
    # ------------------------------------------------------------------ #

    def calculate_all_state_taxes(
        self,
        federal_taxable_income: Decimal,
        allocations: dict[str, Decimal],
        filing_status: str | FilingStatus = "",
        long_term_gains_by_state: Optional[dict[str, Decimal]] = None,
    ) -> dict[str, Decimal]:
        """Calculate state tax for each state in *allocations*.

        Parameters
        ----------
        federal_taxable_income
            Used for rate look-ups (some states use federal AGI).
        allocations
            State → allocated taxable income.
        filing_status
            Override filing status (string or enum).
        long_term_gains_by_state
            Optional per-state LTCG amounts (needed for WA cap-gains tax).

        Returns
        -------
        dict mapping state code → tax amount.
        """
        fs = self._resolve_filing_status(filing_status)
        ltcg = long_term_gains_by_state or {}
        taxes: dict[str, Decimal] = {}

        for state, income in allocations.items():
            if income <= 0:
                taxes[state] = Decimal("0")
                continue

            if state == "CA":
                taxes[state] = calculate_california_tax(income, fs)
            elif state == "NY":
                ny_tax = calculate_ny_tax(income, fs)
                if self.is_nyc_resident:
                    ny_tax += calculate_nyc_tax(income, fs)
                taxes[state] = ny_tax
            elif state == "WA":
                # WA has no income tax; only cap-gains tax
                state_ltcg = ltcg.get("WA", Decimal("0"))
                taxes[state] = calculate_wa_capital_gains_tax(state_ltcg)
            else:
                # Placeholder: flat 5% estimate for other states
                taxes[state] = (income * Decimal("0.05")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

        return taxes

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _resolve_filing_status(self, fs: str | FilingStatus) -> FilingStatus:
        if isinstance(fs, FilingStatus):
            return fs
        if fs and isinstance(fs, str):
            try:
                return FilingStatus(fs)
            except ValueError:
                pass
        return self.filing_status
