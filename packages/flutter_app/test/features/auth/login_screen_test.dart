import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/features/auth/login_screen.dart';
import 'package:taxlens_app/core/providers/auth_provider.dart';

void main() {
  Widget buildApp() {
    return ProviderScope(
      overrides: [
        supabaseAvailableProvider.overrideWith((ref) => false),
      ],
      child: const MaterialApp(home: LoginScreen()),
    );
  }

  testWidgets('Shows TaxLens branding', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('TaxLens'), findsOneWidget);
    expect(find.text('Smart Tax Analysis & Planning'), findsOneWidget);
  });

  testWidgets('Shows Google and Apple sign-in buttons', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Continue with Google'), findsOneWidget);
    expect(find.text('Continue with Apple'), findsOneWidget);
  });

  testWidgets('Shows email form when tapped', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    // Email form starts hidden
    expect(find.byType(TextField), findsNothing);

    // Tap to expand
    await tester.tap(find.text('Sign in with email'));
    await tester.pumpAndSettle();

    // Now email and password fields should be visible
    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
  });

  testWidgets('Shows continue without account button', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Continue without account'), findsOneWidget);
  });

  testWidgets('Shows forgot password after expanding email form', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Sign in with email'));
    await tester.pumpAndSettle();

    expect(find.text('Forgot password?'), findsOneWidget);
    expect(find.text('Sign in with email link instead'), findsOneWidget);
  });
}
