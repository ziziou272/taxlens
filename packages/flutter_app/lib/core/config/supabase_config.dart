/// Supabase configuration.
/// Values are read from environment variables at build time,
/// or can be overridden at runtime via Settings.
class SupabaseConfig {
  static const String defaultUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: '',
  );

  static const String defaultAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: '',
  );

  /// Returns true if Supabase credentials are configured.
  static bool get isConfigured =>
      defaultUrl.isNotEmpty && defaultAnonKey.isNotEmpty;
}
