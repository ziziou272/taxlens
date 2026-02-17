"""
TaxLens Comprehensive QA Test Suite
TC-01 through TC-29 — 2025 Tax Year

Hand-calculated expected values from taxlens-qa-test-plan.md
Tolerances: ±$1 federal, ±$5 state, ±$0.01 FICA/NIIT
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional

# Engine imports
from taxlens_engine.calculator import calculate_taxes
from taxlens_engine.models import FilingStatus, IncomeBreakdown
from taxlens_engine.new_york import calculate_ny_tax, get_ny_standard_deduction

# ───────────────────────────── helpers ─────────────────────────────────────

def D(v) -> Decimal:
    return Decimal(str(v))

def close(actual: Decimal, expected: Decimal, tol: Decimal) -> bool:
    return abs(actual - expected) <= tol

TOL_FED   = D("1")
TOL_STATE = D("5")
TOL_FICA  = D("0.01")
TOL_NIIT  = D("0.01")
TOL_AMT   = D("1")

def extract_sdi(warnings: list) -> Decimal:
    """Parse CA SDI amount from calculator warnings."""
    for w in warnings:
        m = re.search(r"CA SDI withheld: \$([0-9,]+\.[0-9]+)", w)
        if m:
            return D(m.group(1).replace(",", ""))
    return D("0")

# ───────────────────────────── test result ────────────────────────────────

@dataclass
class TaxResult:
    federal: Decimal
    state: Decimal
    ss: Decimal
    medicare: Decimal
    addl_medicare: Decimal
    niit: Decimal
    amt: Decimal
    sdi: Decimal

@dataclass
class CaseResult:
    tc: str
    desc: str
    status: str          # PASS / FAIL / SKIP
    fields_checked: list
    failures: list
    actual: dict
    expected: dict
    notes: str = ""

# ───────────────────────────── run a single case ──────────────────────────

def run(
    tc: str,
    desc: str,
    income: IncomeBreakdown,
    filing_status: FilingStatus,
    state: Optional[str],
    # expected values — None means "skip this field"
    exp_federal: Optional[Decimal] = None,
    exp_state: Optional[Decimal] = None,
    exp_ss: Optional[Decimal] = None,
    exp_medicare: Optional[Decimal] = None,
    exp_addl_medicare: Optional[Decimal] = None,
    exp_niit: Optional[Decimal] = None,
    exp_amt: Optional[Decimal] = None,
    exp_sdi: Optional[Decimal] = None,
    skip_reason: str = "",
    notes: str = "",
    itemized_deductions: Decimal = D("0"),
) -> CaseResult:
    if skip_reason:
        return CaseResult(tc, desc, "SKIP", [], [], {}, {}, skip_reason)

    result = calculate_taxes(
        income, filing_status, state,
        itemized_deductions=itemized_deductions
    )
    actual = TaxResult(
        federal       = result.federal_tax_total,
        state         = result.state_tax,
        ss            = result.social_security_tax,
        medicare      = result.medicare_tax,
        addl_medicare = result.additional_medicare_tax,
        niit          = result.niit,
        amt           = result.amt_owed,
        sdi           = extract_sdi(result.warnings),
    )

    checks = {
        "federal"       : (exp_federal,       TOL_FED,   actual.federal),
        "state"         : (exp_state,         TOL_STATE, actual.state),
        "ss"            : (exp_ss,            TOL_FICA,  actual.ss),
        "medicare"      : (exp_medicare,      TOL_FICA,  actual.medicare),
        "addl_medicare" : (exp_addl_medicare, TOL_FICA,  actual.addl_medicare),
        "niit"          : (exp_niit,          TOL_NIIT,  actual.niit),
        "amt"           : (exp_amt,           TOL_AMT,   actual.amt),
        "sdi"           : (exp_sdi,           TOL_FICA,  actual.sdi),
    }

    fields_checked = []
    failures = []
    for field, (exp, tol, act) in checks.items():
        if exp is None:
            continue
        fields_checked.append(field)
        if not close(act, exp, tol):
            delta = act - exp
            failures.append(f"{field}: actual={act} expected={exp} delta={delta:+}")

    status = "PASS" if not failures else "FAIL"

    return CaseResult(
        tc=tc,
        desc=desc,
        status=status,
        fields_checked=fields_checked,
        failures=failures,
        actual={k: str(getattr(actual, k)) for k in vars(actual)},
        expected={
            "federal"       : str(exp_federal)       if exp_federal       is not None else None,
            "state"         : str(exp_state)          if exp_state          is not None else None,
            "ss"            : str(exp_ss)             if exp_ss             is not None else None,
            "medicare"      : str(exp_medicare)       if exp_medicare       is not None else None,
            "addl_medicare" : str(exp_addl_medicare)  if exp_addl_medicare  is not None else None,
            "niit"          : str(exp_niit)           if exp_niit           is not None else None,
            "amt"           : str(exp_amt)            if exp_amt            is not None else None,
            "sdi"           : str(exp_sdi)            if exp_sdi            is not None else None,
        },
        notes=notes,
    )


# ─────────────────────────────── test cases ───────────────────────────────

def run_all() -> list:
    results = []

    # TC-01: Single W-2 $150K, CA
    # Federal: $25,247 | CA: $9,977.14 | SS: $9,300 | Medicare: $2,175 | SDI: $1,650
    results.append(run(
        "TC-01", "Single $150K W-2, CA",
        IncomeBreakdown(w2_wages=D("150000")),
        FilingStatus.SINGLE, "CA",
        exp_federal=D("25247.00"),
        exp_state=D("9977.14"),
        exp_ss=D("9300.00"),
        exp_medicare=D("2175.00"),
        exp_addl_medicare=D("0"),
        exp_niit=D("0"),
        exp_amt=D("0"),
        exp_sdi=D("1650.00"),
    ))

    # TC-02: MFJ $450K (W-2 $400K + RSU $50K), NY
    # Federal: $88,526 | NY state: $25,838 (NY NOT integrated → will FAIL)
    # Note: FICA per-spouse SS would be $21,836, but engine calculates one cap only
    results.append(run(
        "TC-02", "MFJ $450K (W-2+RSU), NY",
        IncomeBreakdown(w2_wages=D("400000"), rsu_income=D("50000")),
        FilingStatus.MARRIED_JOINTLY, "NY",
        exp_federal=D("88526.00"),
        exp_state=D("25838.13"),   # Correct NY MFJ calc; engine returns $0 → FAIL
        exp_niit=D("0"),
        exp_amt=D("0"),
        notes="NY state not integrated in calculator.py. FICA per-spouse design gap noted separately.",
    ))

    # TC-03: Single $500K W-2+RSU + $100K ISO exercise, CA (no AMT — regular > TMT)
    results.append(run(
        "TC-03", "Single $500K W-2/RSU + $100K ISO, CA — no AMT",
        IncomeBreakdown(w2_wages=D("300000"), rsu_income=D("200000"), iso_bargain_element=D("100000")),
        FilingStatus.SINGLE, "CA",
        exp_federal=D("139297.25"),
        exp_state=D("44481.88"),
        exp_ss=D("10918.20"),
        exp_medicare=D("7250.00"),
        exp_addl_medicare=D("2700.00"),
        exp_niit=D("0"),
        exp_amt=D("0"),
    ))

    # TC-04: HoH $180K W-2 + $30K LTCG, WA
    # HoH ordinary tax (correct brackets): $28,908 + LTCG $4,500 = $33,408
    # NOTE: test plan had $30,647 for ordinary using Single cumulative — that's an error in the plan
    results.append(run(
        "TC-04", "HoH $180K W-2 + $30K LTCG, WA",
        IncomeBreakdown(w2_wages=D("180000"), long_term_gains=D("30000")),
        FilingStatus.HEAD_OF_HOUSEHOLD, "WA",
        exp_federal=D("33408.00"),  # HoH ordinary $28,908 + LTCG $4,500
        exp_state=D("0"),
        exp_ss=D("10918.20"),
        exp_medicare=D("2610.00"),
        exp_addl_medicare=D("0"),
        exp_niit=D("380.00"),
        exp_amt=D("0"),
        notes="HoH ordinary tax = $28,908 (HoH brackets, NOT Single). Test plan erroneously used Single cumulative.",
    ))

    # TC-05: Single $800K W-2 + $100K LTCG, CA
    # SDI should be $8,800 (no cap 2025), engine uses old $153,164 cap → SDI FAIL
    results.append(run(
        "TC-05", "Single $800K W-2 + $100K LTCG, CA",
        IncomeBreakdown(w2_wages=D("800000"), long_term_gains=D("100000")),
        FilingStatus.SINGLE, "CA",
        exp_federal=D("267470.25"),  # $247,470.25 ordinary + $20,000 LTCG
        exp_state=D("91413.34"),     # Engine value (plan says $91,414.34, diff=$1.00 due to plan arithmetic)
        exp_ss=D("10918.20"),
        exp_medicare=D("11600.00"),
        exp_addl_medicare=D("5400.00"),
        exp_niit=D("3800.00"),
        exp_amt=D("0"),
        exp_sdi=D("8800.00"),       # 2025 unlimited SDI; engine has $153,164 cap → FAIL
        notes="SDI expected $8,800 (no 2025 wage cap); engine returns $1,684.80 (old $153,164 cap) → BUG.",
    ))

    # TC-06: Part-year CA→WA SKIP (multi-state not supported)
    results.append(run(
        "TC-06", "Part-year CA→WA $250K",
        IncomeBreakdown(),
        FilingStatus.SINGLE, None,
        skip_reason="Multi-state part-year not supported by single-state calculator",
    ))

    # TC-07: Single $330K (W-2+RSU+NSO) + $40K ISO, CA — no AMT
    results.append(run(
        "TC-07", "Single $330K multi-equity + $40K ISO, CA — no AMT",
        IncomeBreakdown(w2_wages=D("200000"), rsu_income=D("80000"), nso_income=D("50000"), iso_bargain_element=D("40000")),
        FilingStatus.SINGLE, "CA",
        exp_federal=D("79797.25"),
        exp_ss=D("10918.20"),
        exp_medicare=D("4785.00"),
        exp_addl_medicare=D("1170.00"),
        exp_amt=D("0"),
    ))

    # TC-08: Zero income
    results.append(run(
        "TC-08", "Zero income",
        IncomeBreakdown(),
        FilingStatus.SINGLE, "CA",
        exp_federal=D("0"),
        exp_state=D("0"),
        exp_ss=D("0"),
        exp_medicare=D("0"),
        exp_addl_medicare=D("0"),
        exp_niit=D("0"),
        exp_amt=D("0"),
    ))

    # TC-09: Exactly at SS wage base $176,100, Single, WA
    results.append(run(
        "TC-09", "Exactly at SS wage base $176,100",
        IncomeBreakdown(w2_wages=D("176100")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("31511.00"),
        exp_ss=D("10918.20"),
        exp_medicare=D("2553.45"),
        exp_addl_medicare=D("0"),
    ))

    # TC-10: $1 over SS wage base $176,101 — SS must stay capped
    results.append(run(
        "TC-10", "$1 over SS wage base $176,101",
        IncomeBreakdown(w2_wages=D("176101")),
        FilingStatus.SINGLE, "WA",
        exp_ss=D("10918.20"),    # Same — capped
        exp_medicare=D("2553.46"),
        exp_addl_medicare=D("0"),
        notes="SS must NOT increase above $10,918.20. Medicare increases by $0.01.",
    ))

    # TC-11: Exactly at 37% bracket boundary — taxable = $626,350
    results.append(run(
        "TC-11", "Exactly at 37% bracket boundary, Single $641,350 W-2",
        IncomeBreakdown(w2_wages=D("641350")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("188769.75"),
    ))

    # TC-12: $1 into 37% bracket — taxable = $626,351
    results.append(run(
        "TC-12", "$1 into 37% bracket, Single $641,351 W-2",
        IncomeBreakdown(w2_wages=D("641351")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("188770.12"),
    ))

    # TC-13: NIIT boundary — MFJ W-2 $200K + LTCG $50K → AGI exactly $250K = threshold
    results.append(run(
        "TC-13", "NIIT at exact threshold, MFJ AGI=$250K",
        IncomeBreakdown(w2_wages=D("200000"), long_term_gains=D("50000")),
        FilingStatus.MARRIED_JOINTLY, "WA",
        exp_niit=D("0"),
    ))

    # TC-14: $1 over NIIT threshold — MFJ W-2 $200K + LTCG $50,001
    results.append(run(
        "TC-14", "NIIT $1 over MFJ threshold ($250,001)",
        IncomeBreakdown(w2_wages=D("200000"), long_term_gains=D("50001")),
        FilingStatus.MARRIED_JOINTLY, "WA",
        exp_niit=D("0.04"),
    ))

    # TC-15: Additional Medicare at exact $200K boundary, Single — should be $0
    results.append(run(
        "TC-15", "Additional Medicare at exact $200K (single)",
        IncomeBreakdown(w2_wages=D("200000")),
        FilingStatus.SINGLE, "WA",
        exp_addl_medicare=D("0"),
    ))

    # TC-16: Additional Medicare $1 over — Single $200,001
    results.append(run(
        "TC-16", "Additional Medicare $1 over $200K (single $200,001)",
        IncomeBreakdown(w2_wages=D("200001")),
        FilingStatus.SINGLE, "WA",
        exp_addl_medicare=D("0.01"),
    ))

    # TC-17: AMT crossover — Single $80K W-2 + $200K ISO
    # Regular tax = $9,214; TMT = $45,994 → AMT owed = $36,780
    results.append(run(
        "TC-17", "AMT crossover — Single $80K W-2 + $200K ISO",
        IncomeBreakdown(w2_wages=D("80000"), iso_bargain_element=D("200000")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("45994.00"),   # regular $9,214 + AMT $36,780
        exp_amt=D("36780.00"),
    ))

    # TC-18: LTCG 0% stacking — ordinary fills exactly to $48,350 → all LTCG at 15%
    # Ordinary taxable $48,350 → tax $5,563.50; LTCG $20K × 15% = $3,000
    results.append(run(
        "TC-18", "LTCG 0% bracket — no room (ordinary fills to $48,350)",
        IncomeBreakdown(w2_wages=D("63350"), long_term_gains=D("20000")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("8563.50"),   # $5,563.50 ordinary + $3,000 LTCG
        notes="Ordinary taxable=$48,350 (exactly at 0% LTCG limit). All $20K LTCG at 15%.",
    ))

    # TC-19: LTCG 0% stacking — $18,350 at 0%, $1,650 at 15%
    # Ordinary taxable $30K; LTCG: $18,350 × 0% + $1,650 × 15% = $247.50
    results.append(run(
        "TC-19", "LTCG 0% bracket — partial room ($18,350 at 0%, $1,650 at 15%)",
        IncomeBreakdown(w2_wages=D("45000"), long_term_gains=D("20000")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("3609.00"),   # $3,361.50 ordinary + $247.50 LTCG
        notes="Ordinary=$30K. Room in 0% bracket=$18,350. Remaining $1,650 at 15%=$247.50.",
    ))

    # TC-20: MFS $200K W-2, NY
    # Federal: $37,247 | NY state not integrated → $0 returned (FAIL)
    # NY correct: taxable=$192K → $10,951.75
    results.append(run(
        "TC-20", "MFS $200K W-2, NY",
        IncomeBreakdown(w2_wages=D("200000")),
        FilingStatus.MARRIED_SEPARATELY, "NY",
        exp_federal=D("37247.00"),
        exp_state=D("10951.75"),   # NY MFS calc correct; engine returns $0 → FAIL
        notes="NY not integrated in calculator.py → state_tax=$0 instead of $10,951.75.",
    ))

    # TC-21: ESPP qualified disposition — per-share analysis (no IncomeBreakdown field)
    results.append(run(
        "TC-21", "ESPP qualified disposition",
        IncomeBreakdown(),
        FilingStatus.SINGLE, "WA",
        skip_reason="ESPP qualified: per-share analysis; income components map to nso_income+long_term_gains but no dedicated ESPP field in IncomeBreakdown",
    ))

    # TC-22: ESPP disqualifying disposition
    results.append(run(
        "TC-22", "ESPP disqualifying disposition",
        IncomeBreakdown(),
        FilingStatus.SINGLE, "WA",
        skip_reason="ESPP disqualifying: same as above — can be mapped to nso_income+short_term_gains",
    ))

    # TC-23: $2M W-2, Single, CA — top brackets + Mental Health surtax
    # SDI bug: engine caps at $153,164 → gives $1,684.80 instead of $22,000
    results.append(run(
        "TC-23", "Single $2M W-2, CA — top brackets + Mental Health",
        IncomeBreakdown(w2_wages=D("2000000")),
        FilingStatus.SINGLE, "CA",
        exp_federal=D("691470.25"),
        exp_state=D("236657.94"),   # Engine value (plan says $236,658.04, ±$0.10 arithmetic)
        exp_ss=D("10918.20"),
        exp_medicare=D("29000.00"),
        exp_addl_medicare=D("16200.00"),
        exp_sdi=D("22000.00"),      # 2025 unlimited; engine uses old cap → FAIL
        notes="SDI expected $22,000 (no cap); engine returns $1,684.80 → BUG.",
    ))

    # TC-24: Marriage bonus — MFJ $200K combined (neutral at this level)
    results.append(run(
        "TC-24", "Marriage bonus — MFJ $200K vs two Singles at $100K",
        IncomeBreakdown(w2_wages=D("200000")),
        FilingStatus.MARRIED_JOINTLY, "WA",
        exp_federal=D("27228.00"),
        notes="MFJ $200K = same as 2×Single $100K → no bonus/penalty at this level.",
    ))

    # TC-25: Marriage penalty — MFJ $1M combined (two $500K earners each)
    results.append(run(
        "TC-25", "Marriage penalty — MFJ $1M vs two Singles at $500K",
        IncomeBreakdown(w2_wages=D("1000000")),
        FilingStatus.MARRIED_JOINTLY, "WA",
        exp_federal=D("282962.50"),
        notes="MFJ $1M tax = $282,963 vs 2×Single $500K = $278,595 → $4,368 marriage penalty.",
    ))

    # TC-26: SALT cap — standard deduction wins over $10K itemized
    # Single $300K CA: state tax ~$23K but SALT cap = $10K < std ded $15K → std ded used
    results.append(run(
        "TC-26", "SALT cap — standard deduction wins over $10K itemized SALT",
        IncomeBreakdown(w2_wages=D("300000")),
        FilingStatus.SINGLE, "CA",
        itemized_deductions=D("10000"),   # SALT-only itemized; std ded $15K > $10K → std ded wins
        exp_federal=D("69297.25"),         # Same as no itemization (std ded = $15K wins)
        notes="SALT cap $10K < standard deduction $15K → standard deduction used. SALT has no impact here.",
    ))

    # TC-27: ISO qualified sale — $100K ISO at exercise (AMT pref only), $50K LTCG at sale
    # Regular: LTCG $247.50 (first $48,350 at 0%, remaining $1,650 at 15%)
    # AMT: AMTI=$100K; exempt=$88,100; taxable=$11,900; TMT=$3,094
    # AMT owed: $3,094 - $247.50 = $2,846.50
    results.append(run(
        "TC-27", "ISO qualified: $100K AMT pref + $50K LTCG at sale",
        IncomeBreakdown(iso_bargain_element=D("100000"), long_term_gains=D("50000")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("3094.00"),    # $247.50 LTCG tax + $2,846.50 AMT
        exp_amt=D("2846.50"),
        notes="ISO exercise: no ordinary income. $100K creates AMT preference. LTCG mostly at 0%.",
    ))

    # TC-28: NSO exercise $100K spread (ordinary income) + $50K LTCG at sale
    # Ordinary: $100K - $15K = $85K → tax $13,614
    # LTCG: $50K at 15% = $7,500 (ordinary fills past $48,350 0% threshold)
    # FICA: NSO wages $100K → SS $6,200, Medicare $1,450
    results.append(run(
        "TC-28", "NSO exercise $100K spread + $50K LTCG at sale",
        IncomeBreakdown(nso_income=D("100000"), long_term_gains=D("50000")),
        FilingStatus.SINGLE, "WA",
        exp_federal=D("21114.00"),   # $13,614 ordinary + $7,500 LTCG
        exp_ss=D("6200.00"),         # NSO $100K × 6.2% (under SS base)
        exp_medicare=D("1450.00"),   # NSO $100K × 1.45%
        exp_addl_medicare=D("0"),    # Under $200K threshold
        notes="NSO income subject to FICA. LTCG not subject to FICA. LTCG at 15% (ordinary > 0% limit).",
    ))

    # TC-29: MFS $130K — Additional Medicare $45 (MFS threshold = $125K, NOT $200K)
    # Current engine uses single threshold ($200K) → returns $0 → FAIL
    results.append(run(
        "TC-29", "MFS $130K — Additional Medicare $45",
        IncomeBreakdown(w2_wages=D("130000")),
        FilingStatus.MARRIED_SEPARATELY, "WA",
        exp_addl_medicare=D("45.00"),   # 0.9% × ($130K - $125K) = $45
        notes="MFS threshold = $125K (not $200K). Engine uses single threshold → returns $0 → BUG.",
    ))

    return results


# ─────────────────────────────── report ──────────────────────────────────

def print_report(results: list) -> tuple:
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    skipped = sum(1 for r in results if r.status == "SKIP")
    non_skipped = total - skipped

    print("\n" + "="*72)
    print("TAXLENS QA TEST RESULTS — 2025 Tax Year")
    print("="*72)
    print(f"Total: {total}  PASS: {passed}  FAIL: {failed}  SKIP: {skipped}")
    print("-"*72)

    for r in results:
        icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭ "}.get(r.status, "?")
        print(f"\n{icon} {r.tc}: {r.desc}")
        if r.status == "SKIP":
            print(f"   SKIPPED: {r.notes}")
            continue
        if r.status == "PASS":
            checked = ", ".join(r.fields_checked)
            print(f"   Checked: {checked}")
        else:
            for f in r.failures:
                print(f"   FAIL → {f}")
            if r.notes:
                print(f"   NOTE: {r.notes}")

    print("\n" + "="*72)
    print(f"SUMMARY: {passed}/{non_skipped} non-skipped tests passed ({skipped} skipped)")
    print("="*72)
    return passed, failed, skipped


if __name__ == "__main__":
    results = run_all()
    passed, failed, skipped = print_report(results)

    # Save raw JSON
    raw = [asdict(r) for r in results]
    out_json = "/root/.openclaw/workspace/taxlens-test-results.json"
    with open(out_json, "w") as f:
        json.dump(raw, f, indent=2, default=str)
    print(f"\n📄 Raw JSON saved to {out_json}")

    sys.exit(0 if failed == 0 else 1)
