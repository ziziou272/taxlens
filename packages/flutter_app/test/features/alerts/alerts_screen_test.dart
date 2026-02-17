import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/features/alerts/alerts_screen.dart';
import 'package:taxlens_app/features/alerts/alerts_provider.dart';
import 'package:taxlens_app/features/dashboard/dashboard_provider.dart';
import 'package:taxlens_app/core/models/alert.dart';

void main() {
  group('Tax Tips Screen', () {
    testWidgets('shows "Tax Tips" in app bar', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(home: const AlertsScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Tax Tips'), findsOneWidget);
    });

    testWidgets('empty state shows feature explanation', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(home: const AlertsScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Personalized tax tips'), findsOneWidget);
      expect(find.textContaining('automatically find ways to save'), findsOneWidget);
      expect(find.textContaining('401(k)'), findsOneWidget);
      expect(find.text('Enter your income to get tips'), findsOneWidget);
    });
  });
}
