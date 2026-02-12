import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import 'auth_provider.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  final baseUrl = ref.watch(apiBaseUrlProvider);
  final supabaseAvailable = ref.watch(supabaseAvailableProvider);
  
  return ApiClient(
    baseUrl: baseUrl,
    supabaseAvailable: supabaseAvailable,
    onUnauthorized: () {
      // Clear auth state on 401 — Supabase SDK will handle sign-out
      if (supabaseAvailable) {
        ref.read(authServiceProvider).signOut();
      }
    },
  );
});

final apiBaseUrlProvider = StateProvider<String>((ref) => 'https://taxlens.ziziou.com');
