import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/features/settings/settings_screen.dart';

void main() {
  Widget buildApp() {
    return const ProviderScope(
      child: MaterialApp(home: SettingsScreen()),
    );
  }

  testWidgets('Filing status dropdown is present', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Filing Status'), findsOneWidget);
    expect(find.text('Single'), findsOneWidget);
  });

  testWidgets('State dropdown is present', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('State'), findsOneWidget);
    expect(find.text('California'), findsOneWidget);
  });

  testWidgets('API URL field is present', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('API Base URL'), findsOneWidget);
    expect(find.text('http://localhost:8100'), findsOneWidget);
  });

  testWidgets('Filing status dropdown works', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    // Tap on the filing status dropdown
    await tester.tap(find.text('Single').first);
    await tester.pumpAndSettle();

    // Select "Head of Household"
    expect(find.text('Head of Household'), findsWidgets);
    await tester.tap(find.text('Head of Household').last);
    await tester.pumpAndSettle();

    expect(find.text('Head of Household'), findsOneWidget);
  });

  testWidgets('State dropdown works', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    // Tap state dropdown
    await tester.tap(find.text('California').first);
    await tester.pumpAndSettle();

    // Select Texas
    expect(find.text('Texas'), findsWidgets);
    await tester.tap(find.text('Texas').last);
    await tester.pumpAndSettle();

    expect(find.text('Texas'), findsOneWidget);
  });
}
