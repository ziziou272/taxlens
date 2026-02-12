import 'package:flutter_riverpod/flutter_riverpod.dart';

final taxBreakdownProvider =
    Provider<List<Map<String, dynamic>>>((ref) {
  return [
    {'label': 'Gross Income', 'amount': 285000.0, 'indent': 0},
    {'label': 'W-2 Salary', 'amount': 185000.0, 'indent': 1},
    {'label': 'RSU Vesting', 'amount': 62000.0, 'indent': 1},
    {'label': 'Capital Gains', 'amount': 28000.0, 'indent': 1},
    {'label': 'Other Income', 'amount': 10000.0, 'indent': 1},
    {'label': 'Adjustments', 'amount': -3000.0, 'indent': 0},
    {'label': 'AGI', 'amount': 282000.0, 'indent': 0},
    {'label': 'Standard Deduction', 'amount': -14600.0, 'indent': 0},
    {'label': 'Taxable Income', 'amount': 267400.0, 'indent': 0},
    {'label': 'Federal Tax', 'amount': 52430.0, 'indent': 0},
    {'label': 'State Tax (CA)', 'amount': 18200.0, 'indent': 0},
    {'label': 'Total Tax', 'amount': 70630.0, 'indent': 0},
    {'label': 'Total Withheld', 'amount': -58000.0, 'indent': 0},
    {'label': 'Amount Owed', 'amount': 12630.0, 'indent': 0},
  ];
});
