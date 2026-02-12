import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/core/models/alert.dart';
import 'package:taxlens_app/core/theme/app_colors.dart';
import 'package:taxlens_app/features/alerts/alerts_provider.dart';
import 'package:taxlens_app/features/alerts/alerts_screen.dart';
import 'package:taxlens_app/features/dashboard/dashboard_provider.dart';
import 'package:taxlens_app/core/api/api_client.dart';
import 'package:taxlens_app/core/models/tax_result.dart';

final _mockAlerts = [
  const Alert(
    id: '0',
    title: 'Underpayment Risk',
    description: 'You may owe penalties.',
    priority: AlertPriority.critical,
  ),
  const Alert(
    id: '1',
    title: 'AMT Warning',
    description: 'Check alternative minimum tax.',
    priority: AlertPriority.warning,
  ),
  const Alert(
    id: '2',
    title: 'Deduction Tip',
    description: 'Consider itemizing deductions.',
    priority: AlertPriority.info,
  ),
];

void main() {
  Widget buildApp({List<Alert> alerts = const []}) {
    return ProviderScope(
      overrides: [
        alertsProvider.overrideWithValue(alerts),
        alertsResultProvider.overrideWith(() => _FakeAlertsResultNotifier(
              alerts.isNotEmpty
                  ? AlertCheckResult(
                      summary: 'Test',
                      alerts: [],
                      hasCritical: alerts.any(
                          (a) => a.priority == AlertPriority.critical),
                    )
                  : null,
            )),
        taxResultProvider
            .overrideWith(() => _FakeTaxResultNotifier()),
      ],
      child: const MaterialApp(home: AlertsScreen()),
    );
  }

  testWidgets('Shows empty state when no alerts', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('No alerts. Calculate your taxes first.'), findsOneWidget);
  });

  testWidgets('Renders alert cards', (tester) async {
    await tester.pumpWidget(buildApp(alerts: _mockAlerts));
    await tester.pumpAndSettle();

    expect(find.text('Underpayment Risk'), findsOneWidget);
    expect(find.text('AMT Warning'), findsOneWidget);
    expect(find.text('Deduction Tip'), findsOneWidget);
  });

  testWidgets('Critical alerts show red border', (tester) async {
    await tester.pumpWidget(buildApp(alerts: [_mockAlerts[0]]));
    await tester.pumpAndSettle();

    final card = tester.widget<Card>(find.byType(Card).first);
    final shape = card.shape as RoundedRectangleBorder;
    final side = shape.side;
    expect(side.color, AppColors.negative);
  });

  testWidgets('Warning alerts show orange border', (tester) async {
    await tester.pumpWidget(buildApp(alerts: [_mockAlerts[1]]));
    await tester.pumpAndSettle();

    final card = tester.widget<Card>(find.byType(Card).first);
    final shape = card.shape as RoundedRectangleBorder;
    final side = shape.side;
    expect(side.color, AppColors.warning);
  });

  testWidgets('Tap alert shows detail text', (tester) async {
    await tester.pumpWidget(buildApp(alerts: [_mockAlerts[0]]));
    await tester.pumpAndSettle();

    expect(find.text('You may owe penalties.'), findsOneWidget);
  });
}

class _FakeAlertsResultNotifier extends AsyncNotifier<AlertCheckResult?>
    implements AlertsResultNotifier {
  final AlertCheckResult? _result;
  _FakeAlertsResultNotifier(this._result);

  @override
  Future<AlertCheckResult?> build() async => _result;

  @override
  Future<void> checkAlerts(taxResult) async {}
}

class _FakeTaxResultNotifier extends AsyncNotifier<TaxResult?>
    implements TaxResultNotifier {
  @override
  Future<TaxResult?> build() async => null;

  @override
  Future<void> calculate() async {}
}
