import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'app.dart';
import 'core/config/supabase_config.dart';
import 'core/providers/auth_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  bool supabaseInitialized = false;

  if (SupabaseConfig.isConfigured) {
    try {
      await Supabase.initialize(
        url: SupabaseConfig.defaultUrl,
        anonKey: SupabaseConfig.defaultAnonKey,
      );
      supabaseInitialized = true;
    } catch (e) {
      debugPrint('Supabase init failed: $e');
    }
  }

  runApp(
    ProviderScope(
      overrides: [
        supabaseAvailableProvider.overrideWith((ref) => supabaseInitialized),
      ],
      child: const TaxLensApp(),
    ),
  );
}
