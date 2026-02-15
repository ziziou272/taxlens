import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'auth_provider.dart';

class UserSettings {
  final String filingStatus;
  final String state;
  final double wages;
  final double rsuIncome;
  final double capitalGainsShort;
  final double capitalGainsLong;
  final double federalWithheld;
  final double stateWithheld;
  final bool onboardingComplete;

  const UserSettings({
    this.filingStatus = 'single',
    this.state = 'CA',
    this.wages = 0,
    this.rsuIncome = 0,
    this.capitalGainsShort = 0,
    this.capitalGainsLong = 0,
    this.federalWithheld = 0,
    this.stateWithheld = 0,
    this.onboardingComplete = false,
  });

  UserSettings copyWith({
    String? filingStatus,
    String? state,
    double? wages,
    double? rsuIncome,
    double? capitalGainsShort,
    double? capitalGainsLong,
    double? federalWithheld,
    double? stateWithheld,
    bool? onboardingComplete,
  }) {
    return UserSettings(
      filingStatus: filingStatus ?? this.filingStatus,
      state: state ?? this.state,
      wages: wages ?? this.wages,
      rsuIncome: rsuIncome ?? this.rsuIncome,
      capitalGainsShort: capitalGainsShort ?? this.capitalGainsShort,
      capitalGainsLong: capitalGainsLong ?? this.capitalGainsLong,
      federalWithheld: federalWithheld ?? this.federalWithheld,
      stateWithheld: stateWithheld ?? this.stateWithheld,
      onboardingComplete: onboardingComplete ?? this.onboardingComplete,
    );
  }

  TaxInput toTaxInput() => TaxInput(
        filingStatus: filingStatus,
        wages: wages,
        rsuIncome: rsuIncome,
        capitalGainsShort: capitalGainsShort,
        capitalGainsLong: capitalGainsLong,
        state: state,
        federalWithheld: federalWithheld,
        stateWithheld: stateWithheld,
      );

  double get totalIncome => wages + rsuIncome + capitalGainsShort + capitalGainsLong;

  Map<String, dynamic> toSupabaseRow(String userId) => {
        'id': userId,
        'filing_status': filingStatus,
        'state': state,
        'wages': wages,
        'rsu_income': rsuIncome,
        'capital_gains_short': capitalGainsShort,
        'capital_gains_long': capitalGainsLong,
        'federal_withheld': federalWithheld,
        'state_withheld': stateWithheld,
        'onboarding_complete': onboardingComplete,
      };

  factory UserSettings.fromSupabaseRow(Map<String, dynamic> row) {
    return UserSettings(
      filingStatus: row['filing_status'] as String? ?? 'single',
      state: row['state'] as String? ?? 'CA',
      wages: (row['wages'] as num?)?.toDouble() ?? 0,
      rsuIncome: (row['rsu_income'] as num?)?.toDouble() ?? 0,
      capitalGainsShort: (row['capital_gains_short'] as num?)?.toDouble() ?? 0,
      capitalGainsLong: (row['capital_gains_long'] as num?)?.toDouble() ?? 0,
      federalWithheld: (row['federal_withheld'] as num?)?.toDouble() ?? 0,
      stateWithheld: (row['state_withheld'] as num?)?.toDouble() ?? 0,
      onboardingComplete: row['onboarding_complete'] as bool? ?? false,
    );
  }
}

final settingsProvider =
    StateNotifierProvider<SettingsNotifier, UserSettings>((ref) {
  return SettingsNotifier(ref);
});

class SettingsNotifier extends StateNotifier<UserSettings> {
  SettingsNotifier(this._ref) : super(const UserSettings()) {
    _loadSettings();
    // Listen for auth changes to sync settings
    _ref.listen(currentUserProvider, (prev, next) {
      if (next != null && prev == null) {
        // User just logged in — load from Supabase
        _loadFromSupabase(next.id);
      }
    });
  }

  final Ref _ref;
  bool _syncing = false;

  bool get _supabaseAvailable => _ref.read(supabaseAvailableProvider);
  User? get _currentUser =>
      _supabaseAvailable ? Supabase.instance.client.auth.currentUser : null;

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    state = state.copyWith(
      onboardingComplete: prefs.getBool('onboardingComplete') ?? false,
      filingStatus: prefs.getString('filingStatus') ?? 'single',
      state: prefs.getString('state') ?? 'CA',
      wages: prefs.getDouble('wages') ?? 0,
      rsuIncome: prefs.getDouble('rsuIncome') ?? 0,
      capitalGainsShort: prefs.getDouble('capitalGainsShort') ?? 0,
      capitalGainsLong: prefs.getDouble('capitalGainsLong') ?? 0,
      federalWithheld: prefs.getDouble('federalWithheld') ?? 0,
      stateWithheld: prefs.getDouble('stateWithheld') ?? 0,
    );

    // If already logged in, try loading from Supabase
    final user = _currentUser;
    if (user != null) {
      await _loadFromSupabase(user.id);
    }
  }

  Future<void> _loadFromSupabase(String userId) async {
    if (!_supabaseAvailable) return;
    try {
      final response = await Supabase.instance.client
          .from('user_settings')
          .select()
          .eq('id', userId)
          .maybeSingle();
      if (response != null) {
        state = UserSettings.fromSupabaseRow(response);
        // Also update local prefs as cache
        await _saveToLocal();
      } else {
        // No remote settings yet — push current local settings
        await _saveToSupabase();
      }
    } catch (e) {
      debugPrint('Failed to load settings from Supabase: $e');
    }
  }

  Future<void> _saveToLocal() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboardingComplete', state.onboardingComplete);
    await prefs.setString('filingStatus', state.filingStatus);
    await prefs.setString('state', state.state);
    await prefs.setDouble('wages', state.wages);
    await prefs.setDouble('rsuIncome', state.rsuIncome);
    await prefs.setDouble('capitalGainsShort', state.capitalGainsShort);
    await prefs.setDouble('capitalGainsLong', state.capitalGainsLong);
    await prefs.setDouble('federalWithheld', state.federalWithheld);
    await prefs.setDouble('stateWithheld', state.stateWithheld);
  }

  Future<void> _saveToSupabase() async {
    if (!_supabaseAvailable || _syncing) return;
    final user = _currentUser;
    if (user == null) return;
    _syncing = true;
    try {
      await Supabase.instance.client
          .from('user_settings')
          .upsert(state.toSupabaseRow(user.id));
    } catch (e) {
      debugPrint('Failed to save settings to Supabase: $e');
    } finally {
      _syncing = false;
    }
  }

  Future<void> _persist() async {
    await _saveToLocal();
    await _saveToSupabase();
  }

  void update(UserSettings Function(UserSettings) updater) {
    state = updater(state);
    _persist();
  }

  void setFilingStatus(String v) {
    state = state.copyWith(filingStatus: v);
    _persist();
  }

  void setState(String v) {
    state = state.copyWith(state: v);
    _persist();
  }

  void setWages(double v) {
    state = state.copyWith(wages: v);
    _persist();
  }

  void setRsuIncome(double v) {
    state = state.copyWith(rsuIncome: v);
    _persist();
  }

  void setCapitalGainsShort(double v) {
    state = state.copyWith(capitalGainsShort: v);
    _persist();
  }

  void setCapitalGainsLong(double v) {
    state = state.copyWith(capitalGainsLong: v);
    _persist();
  }

  void setFederalWithheld(double v) {
    state = state.copyWith(federalWithheld: v);
    _persist();
  }

  void setStateWithheld(double v) {
    state = state.copyWith(stateWithheld: v);
    _persist();
  }

  Future<void> setOnboardingComplete(bool v) async {
    state = state.copyWith(onboardingComplete: v);
    await _persist();
  }
}
