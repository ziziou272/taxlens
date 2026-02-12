"""
End-to-end integration tests for multi-state income sourcing.

Each scenario sets up a complete taxpayer situation, runs the
MultiStateCalculator, and verifies state-by-state tax amounts.
"""

from datetime import date
from decimal import Decimal

import pytest

from taxlens_engine.models import FilingStatus
from taxlens_engine.multi_state import MultiStateCalculator, StatePresence


# ── Scenario 1: CA→WA mid-year move ──────────────────────────────────


class TestCAtoWAMidYearMove:
    """Employee moves from CA to WA on July 1.
    $300K salary, $100K RSU vest.
    Partial-year CA tax + WA capital gains (none here — RSU is ordinary).
    """

    @pytest.fixture()
    def calc(self):
        return MultiStateCalculator(
            presences=[
                StatePresence("CA", days=181, work_days=125),
                StatePresence("WA", days=184, work_days=127),
            ],
            move_date=date(2025, 7, 1),
            filing_status=FilingStatus.SINGLE,
        )

    def test_residency(self, calc):
        # Neither state hits 183+ except WA (184)
        assert calc.determine_residency() == ["WA"]

    def test_part_year_detected(self, calc):
        move = calc.detect_part_year_move()
        assert move is not None
        assert move[2] == date(2025, 7, 1)

    def test_salary_allocation(self, calc):
        alloc = calc.allocate_income(Decimal("300000"))
        # ~125/252 ≈ 49.6% to CA, ~127/252 ≈ 50.4% to WA
        assert Decimal("140000") < alloc["CA"] < Decimal("160000")
        assert Decimal("140000") < alloc["WA"] < Decimal("165000")

    def test_rsu_allocation(self, calc):
        # RSU granted 2 years ago while in CA, vest July 2025
        rsu_alloc = calc.allocate_equity_income(
            equity_income=Decimal("100000"),
            grant_date=date(2023, 7, 1),
            vest_date=date(2025, 7, 1),
            work_days_by_state={"CA": 500, "WA": 0},
        )
        # All RSU income sourced to CA (worked in CA entire grant→vest)
        assert rsu_alloc["CA"] == Decimal("100000.00")

    def test_taxes(self, calc):
        salary_alloc = calc.allocate_income(Decimal("300000"))
        rsu_alloc = calc.allocate_equity_income(
            equity_income=Decimal("100000"),
            grant_date=date(2023, 7, 1),
            vest_date=date(2025, 7, 1),
            work_days_by_state={"CA": 500, "WA": 0},
        )
        # Combine allocations
        combined = {}
        for st in {"CA", "WA"}:
            combined[st] = salary_alloc.get(st, Decimal("0")) + rsu_alloc.get(st, Decimal("0"))

        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("400000"),
            allocations=combined,
        )
        # CA should have significant tax on ~$250K
        assert taxes["CA"] > Decimal("15000")
        # WA has no income tax (no LTCG here)
        assert taxes["WA"] == Decimal("0")
        # Total state tax is reasonable
        total = sum(taxes.values())
        assert Decimal("15000") < total < Decimal("40000")


# ── Scenario 2: NY+NYC resident full year ────────────────────────────


class TestNYCResidentFullYear:
    """$500K income + $200K RSU in NYC. Full NY + NYC tax."""

    @pytest.fixture()
    def calc(self):
        return MultiStateCalculator(
            presences=[StatePresence("NY", days=365, work_days=250)],
            filing_status=FilingStatus.SINGLE,
            is_nyc_resident=True,
        )

    def test_residency(self, calc):
        assert calc.determine_residency() == ["NY"]

    def test_full_allocation(self, calc):
        alloc = calc.allocate_income(Decimal("700000"))
        assert alloc["NY"] == Decimal("700000.00")

    def test_taxes(self, calc):
        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("700000"),
            allocations={"NY": Decimal("700000")},
        )
        # NY state ~$47K + NYC ~$27K ≈ $74K range
        assert taxes["NY"] > Decimal("50000")
        assert taxes["NY"] < Decimal("100000")


# ── Scenario 3: WA resident, CA RSU sourcing ─────────────────────────


class TestWAResidentCARSU:
    """Lives in WA, RSUs granted while working in CA."""

    @pytest.fixture()
    def calc(self):
        return MultiStateCalculator(
            presences=[StatePresence("WA", days=365, work_days=250)],
            filing_status=FilingStatus.SINGLE,
        )

    def test_rsu_sourced_to_ca(self, calc):
        alloc = calc.allocate_equity_income(
            equity_income=Decimal("150000"),
            grant_date=date(2022, 1, 1),
            vest_date=date(2025, 1, 1),
            work_days_by_state={"CA": 500, "WA": 250},
        )
        # 500/750 = 66.7% to CA
        assert alloc["CA"] == Decimal("100000.00")
        assert alloc["WA"] == Decimal("50000.00")

    def test_taxes_on_ca_sourced(self, calc):
        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("100000"),
            allocations={"CA": Decimal("100000")},
        )
        # CA tax on $100K single ≈ $5-6K
        assert Decimal("3000") < taxes["CA"] < Decimal("8000")


# ── Scenario 4: Remote worker ────────────────────────────────────────


class TestRemoteWorker:
    """Lives in WA, works for NY company, 30 days in NY office."""

    @pytest.fixture()
    def calc(self):
        return MultiStateCalculator(
            presences=[
                StatePresence("WA", days=335, work_days=220),
                StatePresence("NY", days=30, work_days=30),
            ],
            filing_status=FilingStatus.SINGLE,
        )

    def test_residency(self, calc):
        # WA has 335 days → resident
        assert calc.determine_residency() == ["WA"]

    def test_ny_source_allocation(self, calc):
        alloc = calc.allocate_income(Decimal("250000"))
        # 30/250 = 12% to NY
        assert alloc["NY"] == Decimal("30000.00")
        assert alloc["WA"] == Decimal("220000.00")

    def test_taxes(self, calc):
        alloc = calc.allocate_income(Decimal("250000"))
        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("250000"),
            allocations=alloc,
        )
        # NY tax on $30K source income
        assert taxes["NY"] > Decimal("1000")
        assert taxes["NY"] < Decimal("5000")
        # WA no income tax
        assert taxes["WA"] == Decimal("0")


# ── Scenario 5: Triple state ─────────────────────────────────────────


class TestTripleState:
    """CA Jan-Apr, NY May-Aug, WA Sep-Dec. $400K total income."""

    @pytest.fixture()
    def calc(self):
        return MultiStateCalculator(
            presences=[
                StatePresence("CA", days=120, work_days=84),
                StatePresence("NY", days=123, work_days=87),
                StatePresence("WA", days=122, work_days=85),
            ],
            filing_status=FilingStatus.SINGLE,
        )

    def test_no_residency(self, calc):
        # No state hits 183 days
        assert calc.determine_residency() == []

    def test_allocation(self, calc):
        alloc = calc.allocate_income(Decimal("400000"))
        total = sum(alloc.values())
        # Should sum to ~$400K (rounding)
        assert abs(total - Decimal("400000")) < Decimal("1")
        # Roughly equal thirds
        for st in ("CA", "NY", "WA"):
            assert Decimal("120000") < alloc[st] < Decimal("145000")

    def test_taxes(self, calc):
        alloc = calc.allocate_income(Decimal("400000"))
        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("400000"),
            allocations=alloc,
        )
        # CA and NY should have taxes; WA should be $0
        assert taxes["CA"] > Decimal("5000")
        assert taxes["NY"] > Decimal("5000")
        assert taxes["WA"] == Decimal("0")
        total = sum(taxes.values())
        assert Decimal("15000") < total < Decimal("40000")


# ── Scenario 6: High-income multi-state + LTCG ──────────────────────


class TestHighIncomeMultiState:
    """$800K income, RSUs vesting across CA and NY, LTCG in WA >$270K."""

    @pytest.fixture()
    def calc(self):
        return MultiStateCalculator(
            presences=[
                StatePresence("CA", days=150, work_days=105),
                StatePresence("NY", days=100, work_days=70),
                StatePresence("WA", days=115, work_days=80),
            ],
            filing_status=FilingStatus.SINGLE,
        )

    def test_salary_allocation(self, calc):
        alloc = calc.allocate_income(Decimal("500000"))
        assert alloc["CA"] > alloc["NY"]  # More work days
        assert sum(alloc.values()) == Decimal("500000.00")  # exact or close

    def test_rsu_allocation(self, calc):
        rsu_alloc = calc.allocate_equity_income(
            equity_income=Decimal("300000"),
            grant_date=date(2023, 1, 1),
            vest_date=date(2025, 6, 1),
            work_days_by_state={"CA": 300, "NY": 200},
        )
        # 300/500 = 60% CA, 40% NY
        assert rsu_alloc["CA"] == Decimal("180000.00")
        assert rsu_alloc["NY"] == Decimal("120000.00")

    def test_taxes_with_ltcg(self, calc):
        # Salary allocation
        salary_alloc = calc.allocate_income(Decimal("500000"))
        # RSU allocation
        rsu_alloc = calc.allocate_equity_income(
            equity_income=Decimal("300000"),
            grant_date=date(2023, 1, 1),
            vest_date=date(2025, 6, 1),
            work_days_by_state={"CA": 300, "NY": 200},
        )
        # Combine
        combined: dict[str, Decimal] = {}
        for st in ("CA", "NY", "WA"):
            combined[st] = salary_alloc.get(st, Decimal("0")) + rsu_alloc.get(st, Decimal("0"))

        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("800000"),
            allocations=combined,
            long_term_gains_by_state={"WA": Decimal("350000")},
        )
        # CA high tax
        assert taxes["CA"] > Decimal("20000")
        # NY tax
        assert taxes["NY"] > Decimal("5000")
        # WA cap gains: 7% * (350K - 270K) = $5,600
        assert taxes["WA"] == Decimal("5600.00")

        total = sum(taxes.values())
        assert total > Decimal("40000")

    def test_total_across_states(self, calc):
        """Verify total tax across all states is reasonable for $800K income."""
        alloc = calc.allocate_income(Decimal("800000"))
        taxes = calc.calculate_all_state_taxes(
            federal_taxable_income=Decimal("800000"),
            allocations=alloc,
            long_term_gains_by_state={"WA": Decimal("350000")},
        )
        total = sum(taxes.values())
        # Should be between 4% and 12% of total income
        assert Decimal("32000") < total < Decimal("96000")
