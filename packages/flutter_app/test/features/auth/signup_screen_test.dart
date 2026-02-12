import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:taxlens_app/features/auth/signup_screen.dart';
import 'package:taxlens_app/core/providers/auth_provider.dart';

void main() {
  Widget buildApp() {
    return ProviderScope(
      overrides: [
        supabaseAvailableProvider.overrideWith((ref) => false),
      ],
      child: const MaterialApp(home: SignupScreen()),
    );
  }

  testWidgets('Shows signup form fields', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Join TaxLens'), findsOneWidget); // Title text in body
    expect(find.byType(TextField), findsNWidgets(3)); // Email, Password, Confirm Password
    expect(find.widgetWithText(FilledButton, 'Create Account'), findsOneWidget); // The actual button
  });

  testWidgets('Shows link to login', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Already have an account? Sign in'), findsOneWidget);
  });

  testWidgets('Shows ToS notice', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Terms of Service'),
      findsOneWidget,
    );
  });
}
