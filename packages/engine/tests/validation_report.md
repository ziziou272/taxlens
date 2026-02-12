# TaxLens Engine Cross-Validation Report

**Date:** 2026-02-12  
**Tax Year:** 2025  
**Reference:** Hand-computed IRS values using Rev. Proc. 2024-40 (2025 inflation adjustments)  
**Note:** PSLmodels/Tax-Calculator (taxcalc 6.4.0) was installed but `calc_all()` hangs on single-record DataFrames. Reference values were hand-computed using published IRS brackets/rates instead.

## Summary

**Result: ✅ All 20 scenarios match — zero discrepancies found.**

The TaxLens engine correctly implements:
- 2025 federal income tax brackets (all 7 rates: 10%–37%)
- Standard deductions (Single $15K, MFJ $30K, HoH $22.5K)
- Long-term capital gains preferential rates (0%/15%/20% with stacking)
- AMT calculation (26%/28% rates, $88.1K/$137K exemptions, phaseout)
- FICA: Social Security (6.2% up to $176,100 wage base)
- Medicare (1.45%) + Additional Medicare (0.9% over $200K/$250K)
- NIIT (3.8% on lesser of investment income or MAGI over threshold)
- RSU/ESPP income properly classified and taxed

## Scenario Results

| # | Scenario | Fed Income Tax | FICA Total | NIIT | AMT | Total Tax | Eff Rate | Status |
|---|----------|---------------|------------|------|-----|-----------|----------|--------|
| 1 | Single, $75K W2 | $8,114 | $5,738 | $0 | $0 | $13,852 | 18.5% | ✅ |
| 2 | Single, $150K W2 | $25,247 | $11,475 | $0 | $0 | $36,722 | 24.5% | ✅ |
| 3 | MFJ, $150K W2 | $16,228 | $11,475 | $0 | $0 | $27,703 | 18.5% | ✅ |
| 4 | MFJ, $300K W2 | $50,494 | $15,718 | $0 | $0 | $66,212 | 22.1% | ✅ |
| 5 | HoH, $50K W2 | $2,960 | $3,825 | $0 | $0 | $6,785 | 13.6% | ✅ |
| 6 | Single, $200K W2 + $100K RSU | $69,297 | $16,168 | $0 | $0 | $85,465 | 28.5% | ✅ |
| 7 | MFJ, $300K W2 + $200K RSU + $50K LTCG | $112,026 | $20,418 | $1,900 | $0 | $134,344 | 24.4% | ✅ |
| 8 | Single, $250K W2 + ISO $100K bargain | $52,263 | $14,993 | $0 | $12,217 | $79,473 | 31.8% | ✅ |
| 9 | Single, $400K W2 + $30K ESPP disq | $114,797 | $18,518 | $1,140 | $0 | $134,455 | 31.3% | ✅ |
| 10 | MFJ, $500K W2 + $150K RSU + $80K LTCG + $20K STCG | $179,095 | $23,943 | $3,800 | $0 | $206,838 | 27.6% | ✅ |
| 11 | Single, $800K W2 | $247,470 | $27,918 | $0 | $0 | $275,388 | 34.4% | ✅ |
| 12 | MFJ, $1M W2 | $282,963 | $32,168 | $0 | $0 | $315,131 | 31.5% | ✅ |
| 13 | Single, $600K W2 + $200K LTCG | $214,297 | $23,218 | $7,600 | $0 | $245,115 | 30.6% | ✅ |
| 14 | MFJ, $400K W2 + $100K QDIV | $89,494 | $18,068 | $3,800 | $0 | $111,362 | 22.3% | ✅ |
| 15 | Single, $300K W2 + $200K ISO bargain | $69,297 | $16,168 | $0 | $37,183 | $122,648 | 40.9% | ✅ |
| 16 | Single, $160K W2 | $27,647 | $12,240 | $0 | $0 | $39,887 | 24.9% | ✅ |
| 17 | Single, $250K W2 | $52,263 | $14,993 | $0 | $0 | $67,256 | 26.9% | ✅ |
| 18 | MFJ, $350K W2 | $62,494 | $16,893 | $0 | $0 | $79,387 | 22.7% | ✅ |
| 19 | MFJ, $200K, $40K itemized | $25,028 | $13,818 | $0 | $0 | $38,846 | 19.4% | ✅ |
| 20 | Single, $100K W2 | $13,614 | $7,650 | $0 | $0 | $21,264 | 21.3% | ✅ |

## Design Notes & Recommendations

### 1. SALT Cap Not Enforced Internally
The engine accepts `itemized_deductions` as a pre-computed total. It does **not** break down deductions by type or enforce the $10K SALT cap. This is acceptable for now — the caller (API/UI layer) should apply the SALT cap before passing the value. A future enhancement could add a structured `ItemizedDeductions` model with automatic cap enforcement.

### 2. taxcalc Compatibility Issue
PSLmodels/Tax-Calculator v6.4.0 installs successfully but `calc_all()` hangs indefinitely on single-record DataFrames. This appears to be a known issue with the latest version. For future validation, consider pinning to an earlier version or using the `taxcalc` internal functions directly.

### 3. 2025 Parameter Verification
All 2025 parameters in `TaxYear` model were verified against IRS Rev. Proc. 2024-40:
- ✅ Standard deductions: $15,000 (S), $30,000 (MFJ), $22,500 (HoH)
- ✅ SS wage base: $176,100
- ✅ Federal brackets: All 7 thresholds correct for all filing statuses
- ✅ LTCG brackets: Correct for Single and MFJ
- ✅ AMT exemptions: $88,100 (S), $137,000 (MFJ)
- ✅ AMT phaseout: $626,350 (S), $1,252,700 (MFJ)
- ✅ NIIT/Additional Medicare thresholds: $200K (S), $250K (MFJ)

### 4. Test Coverage Added
- 20 parametrized scenarios covering all major tax computation paths
- 4 additional targeted tests (SALT cap behavior, standard vs itemized, FICA on RSU, NIIT thresholds)
- Total: 24 new tests, all passing
- Full suite: 483 tests, 0 failures
