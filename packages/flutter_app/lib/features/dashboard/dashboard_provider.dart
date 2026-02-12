import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/tax_result.dart';

/// Mock data provider for dashboard. Will connect to API later.
final dashboardProvider = Provider<TaxResult>((ref) {
  return const TaxResult(
    totalIncome: 285000,
    federalTax: 52430,
    stateTax: 18200,
    totalTax: 70630,
    effectiveRate: 24.8,
    marginalRate: 32.0,
    totalWithheld: 58000,
    amountOwed: 12630,
    incomeBreakdown: {
      'W-2 Salary': 185000,
      'RSU Vesting': 62000,
      'Capital Gains': 28000,
      'Other': 10000,
    },
  );
});
