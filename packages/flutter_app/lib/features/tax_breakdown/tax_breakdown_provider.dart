import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../dashboard/dashboard_provider.dart';

final taxBreakdownProvider =
    Provider<List<Map<String, dynamic>>>((ref) {
  final resultAsync = ref.watch(taxResultProvider);

  return resultAsync.when(
    data: (result) {
      if (result == null) return _mockBreakdown;
      return [
        {'label': 'Gross Income', 'amount': result.totalIncome, 'indent': 0},
        ...result.incomeBreakdown.entries
            .map((e) => {'label': e.key, 'amount': e.value, 'indent': 1}),
        {'label': 'Standard Deduction', 'amount': -result.deductionUsed, 'indent': 0},
        {'label': 'Taxable Income', 'amount': result.taxableIncome, 'indent': 0},
        {'label': 'Federal Tax', 'amount': result.federalTax, 'indent': 0},
        if (result.socialSecurityTax > 0)
          {'label': 'Social Security', 'amount': result.socialSecurityTax, 'indent': 1},
        if (result.medicareTax > 0)
          {'label': 'Medicare', 'amount': result.medicareTax, 'indent': 1},
        {'label': 'State Tax', 'amount': result.stateTax, 'indent': 0},
        {'label': 'Total Tax', 'amount': result.totalTax, 'indent': 0},
        {'label': 'Total Withheld', 'amount': -result.totalWithheld, 'indent': 0},
        {'label': 'Amount Owed', 'amount': result.amountOwed, 'indent': 0},
      ];
    },
    loading: () => _mockBreakdown,
    error: (_, __) => _mockBreakdown,
  );
});

const _mockBreakdown = <Map<String, dynamic>>[
  {'label': 'Enter income to see breakdown', 'amount': 0.0, 'indent': 0},
];
