"""Unit tests for multi_state module."""

from datetime import date
from decimal import Decimal

import pytest

from taxlens_engine.models import FilingStatus
from taxlens_engine.multi_state import (
    MultiStateCalculator,
    StatePresence,
    RESIDENCY_THRESHOLD,
)


# ── Residency ──────────────────────────────────────────────────────────


def test_determine_residency_single_state():
    calc = MultiStateCalculator(
        presences=[StatePresence("CA", days=365, work_days=250)]
    )
    assert calc.determine_residency() == ["CA"]


def test_determine_residency_none():
    calc = MultiStateCalculator(
        presences=[
            StatePresence("CA", days=100, work_days=70),
            StatePresence("NY", days=100, work_days=70),
            StatePresence("WA", days=100, work_days=70),
        ]
    )
    assert calc.determine_residency() == []


def test_determine_residency_dual():
    calc = MultiStateCalculator(
        presences=[
            StatePresence("CA", days=200, work_days=140),
            StatePresence("NY", days=185, work_days=120),
        ]
    )
    assert set(calc.determine_residency()) == {"CA", "NY"}


# ── Part-year move ─────────────────────────────────────────────────────


def test_detect_part_year_move():
    calc = MultiStateCalculator(
        presences=[
            StatePresence("CA", days=181, work_days=120),
            StatePresence("WA", days=184, work_days=130),
        ],
        move_date=date(2025, 7, 1),
    )
    result = calc.detect_part_year_move()
    assert result is not None
    from_st, to_st, md = result
    assert {from_st, to_st} == {"CA", "WA"}
    assert md == date(2025, 7, 1)


def test_detect_no_move():
    calc = MultiStateCalculator(
        presences=[StatePresence("CA", days=365, work_days=250)]
    )
    assert calc.detect_part_year_move() is None


# ── Income allocation ──────────────────────────────────────────────────


def test_allocate_income_work_days():
    calc = MultiStateCalculator(
        presences=[
            StatePresence("CA", days=181, work_days=100),
            StatePresence("WA", days=184, work_days=150),
        ]
    )
    alloc = calc.allocate_income(Decimal("300000"))
    assert alloc["CA"] == Decimal("120000.00")
    assert alloc["WA"] == Decimal("180000.00")


def test_allocate_income_zero_work_days_fallback():
    calc = MultiStateCalculator(
        presences=[
            StatePresence("CA", days=200, work_days=0),
            StatePresence("WA", days=165, work_days=0),
        ]
    )
    alloc = calc.allocate_income(Decimal("365000"))
    # Falls back to calendar-day ratio
    assert alloc["CA"] > alloc["WA"]


def test_allocate_capital_gains_to_resident():
    calc = MultiStateCalculator(
        presences=[StatePresence("WA", days=365, work_days=250)]
    )
    alloc = calc.allocate_income(Decimal("500000"), income_type="capital_gain")
    assert alloc == {"WA": Decimal("500000")}


# ── Equity allocation ─────────────────────────────────────────────────


def test_allocate_equity_income():
    calc = MultiStateCalculator(presences=[])
    alloc = calc.allocate_equity_income(
        equity_income=Decimal("100000"),
        grant_date=date(2023, 1, 1),
        vest_date=date(2025, 1, 1),
        work_days_by_state={"CA": 400, "WA": 100},
    )
    assert alloc["CA"] == Decimal("80000.00")
    assert alloc["WA"] == Decimal("20000.00")


def test_allocate_equity_income_single_state():
    calc = MultiStateCalculator(presences=[])
    alloc = calc.allocate_equity_income(
        equity_income=Decimal("200000"),
        grant_date=date(2023, 6, 1),
        vest_date=date(2025, 6, 1),
        work_days_by_state={"NY": 500},
    )
    assert alloc == {"NY": Decimal("200000.00")}


def test_allocate_equity_income_zero_days():
    calc = MultiStateCalculator(presences=[])
    alloc = calc.allocate_equity_income(
        equity_income=Decimal("100000"),
        grant_date=date(2023, 1, 1),
        vest_date=date(2025, 1, 1),
        work_days_by_state={},
    )
    assert alloc == {}


# ── Tax calculations ──────────────────────────────────────────────────


def test_calculate_ca_tax():
    calc = MultiStateCalculator(
        presences=[StatePresence("CA", days=365, work_days=250)],
        filing_status=FilingStatus.SINGLE,
    )
    taxes = calc.calculate_all_state_taxes(
        federal_taxable_income=Decimal("300000"),
        allocations={"CA": Decimal("300000")},
    )
    assert taxes["CA"] > Decimal("0")
    # CA tax on $300K single should be roughly $20-25K
    assert Decimal("15000") < taxes["CA"] < Decimal("35000")


def test_calculate_ny_with_nyc():
    calc = MultiStateCalculator(
        presences=[StatePresence("NY", days=365, work_days=250)],
        filing_status=FilingStatus.SINGLE,
        is_nyc_resident=True,
    )
    taxes = calc.calculate_all_state_taxes(
        federal_taxable_income=Decimal("500000"),
        allocations={"NY": Decimal("500000")},
    )
    assert taxes["NY"] > Decimal("25000")  # NY + NYC combined


def test_calculate_wa_no_income_tax():
    calc = MultiStateCalculator(
        presences=[StatePresence("WA", days=365, work_days=250)],
        filing_status=FilingStatus.SINGLE,
    )
    taxes = calc.calculate_all_state_taxes(
        federal_taxable_income=Decimal("300000"),
        allocations={"WA": Decimal("300000")},
    )
    # No income tax, no LTCG passed
    assert taxes["WA"] == Decimal("0")


def test_calculate_wa_with_ltcg():
    calc = MultiStateCalculator(
        presences=[StatePresence("WA", days=365, work_days=250)],
        filing_status=FilingStatus.SINGLE,
    )
    taxes = calc.calculate_all_state_taxes(
        federal_taxable_income=Decimal("400000"),
        allocations={"WA": Decimal("400000")},
        long_term_gains_by_state={"WA": Decimal("350000")},
    )
    # 7% on (350K - 270K) = $5,600
    assert taxes["WA"] == Decimal("5600.00")


def test_other_state_placeholder():
    calc = MultiStateCalculator(
        presences=[StatePresence("TX", days=365, work_days=250)],
        filing_status=FilingStatus.SINGLE,
    )
    taxes = calc.calculate_all_state_taxes(
        federal_taxable_income=Decimal("200000"),
        allocations={"TX": Decimal("200000")},
    )
    # Placeholder 5%
    assert taxes["TX"] == Decimal("10000.00")


def test_zero_income_allocation():
    calc = MultiStateCalculator(
        presences=[StatePresence("CA", days=365, work_days=250)],
    )
    taxes = calc.calculate_all_state_taxes(
        federal_taxable_income=Decimal("0"),
        allocations={"CA": Decimal("0")},
    )
    assert taxes["CA"] == Decimal("0")
