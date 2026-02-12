import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/features/onboarding/onboarding_screen.dart';

void main() {
  Widget buildApp() {
    return ProviderScope(
      child: MaterialApp(
        home: const OnboardingScreen(),
      ),
    );
  }

  testWidgets('Shows step 1 (filing status)', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Filing Status'), findsOneWidget);
    expect(find.text('How do you file your taxes?'), findsOneWidget);
    expect(find.text('Single'), findsOneWidget);
    expect(find.text('Married Filing Jointly'), findsOneWidget);
  });

  testWidgets('Can navigate through steps', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    // Step 1
    expect(find.text('Filing Status'), findsOneWidget);
    expect(find.text('Next'), findsOneWidget);

    // Go to step 2
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();

    expect(find.text('State of Residence'), findsOneWidget);
    expect(find.text('California'), findsOneWidget);

    // Go to step 3
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();

    expect(find.text('Income Range'), findsOneWidget);
    expect(find.text('Get Started'), findsOneWidget);
  });

  testWidgets('Completes onboarding shows Get Started on last step',
      (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    // Navigate to last step
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();

    expect(find.text('Get Started'), findsOneWidget);
    expect(find.text('Income Range'), findsOneWidget);
    expect(find.textContaining('\$100,000 - \$250,000'), findsOneWidget);
  });
}
