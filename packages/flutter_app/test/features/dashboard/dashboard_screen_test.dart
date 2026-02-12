import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/core/models/tax_result.dart';
import 'package:taxlens_app/features/dashboard/dashboard_provider.dart';
import 'package:taxlens_app/features/dashboard/dashboard_screen.dart';

final _mockTaxResult = TaxResult(
  totalIncome: 200000,
  federalTax: 35000,
  stateTax: 12000,
  totalTax: 47000,
  effectiveRate: 23.5,
  marginalRate: 32.0,
  totalWithheld: 40000,
  amountOwed: 7000,
  incomeBreakdown: {
    'W-2 Salary': 150000,
    'RSU Vesting': 50000,
  },
);

void main() {
  Widget buildApp({TaxResult? result}) {
    return ProviderScope(
      overrides: [
        taxResultProvider.overrideWith(() => _FakeTaxResultNotifier(result)),
        alertSummaryProvider
            .overrideWithValue(const AlertSummary(critical: 1, warning: 2)),
      ],
      child: const MaterialApp(home: DashboardScreen()),
    );
  }

  testWidgets('Shows empty state with calculate button when no result',
      (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Enter your income to get started'), findsOneWidget);
    expect(find.text('Enter Income'), findsOneWidget);
  });

  testWidgets('Renders tax summary card with mock data', (tester) async {
    await tester.pumpWidget(buildApp(result: _mockTaxResult));
    await tester.pumpAndSettle();

    expect(find.text('Estimated Total Tax'), findsOneWidget);
    expect(find.textContaining('\$47,000'), findsOneWidget);
    expect(find.text('23.5%'), findsOneWidget);
    expect(find.text('32.0%'), findsOneWidget);
  });

  testWidgets('Renders withholding gap bar', (tester) async {
    await tester.pumpWidget(buildApp(result: _mockTaxResult));
    await tester.pumpAndSettle();

    expect(find.text('Withholding vs Projected'), findsOneWidget);
    expect(find.textContaining('\$40,000'), findsOneWidget);
  });

  testWidgets('Renders income breakdown chart', (tester) async {
    await tester.pumpWidget(buildApp(result: _mockTaxResult));
    await tester.pumpAndSettle();

    expect(find.text('Income Breakdown'), findsOneWidget);
    expect(find.text('W-2 Salary'), findsOneWidget);
    expect(find.text('RSU Vesting'), findsOneWidget);
  });

  testWidgets('Shows Calculate FAB', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Calculate'), findsOneWidget);
    expect(find.byIcon(Icons.calculate), findsOneWidget);
  });
}

class _FakeTaxResultNotifier extends AsyncNotifier<TaxResult?>
    implements TaxResultNotifier {
  final TaxResult? _result;
  _FakeTaxResultNotifier(this._result);

  @override
  Future<TaxResult?> build() async => _result;

  @override
  Future<void> calculate() async {}
}
