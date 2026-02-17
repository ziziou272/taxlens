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

  // Deductions
  final double mortgageInterest;
  final double saltPaid;
  final double charitableContributions;
  final double medicalExpenses;

  // Retirement & Pre-tax
  final double contributions401k;
  final double iraContributions;
  final double hsaContributions;
  final double studentLoanInterest;

  // Family & Education
  final int numChildrenUnder17;
  final int numOtherDependents;
  final double educationExpenses;
  final String educationType;
  final bool ageOver50;

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
    // Deductions
    this.mortgageInterest = 0,
    this.saltPaid = 0,
    this.charitableContributions = 0,
    this.medicalExpenses = 0,
    // Retirement & Pre-tax
    this.contributions401k = 0,
    this.iraContributions = 0,
    this.hsaContributions = 0,
    this.studentLoanInterest = 0,
    // Family & Education
    this.numChildrenUnder17 = 0,
    this.numOtherDependents = 0,
    this.educationExpenses = 0,
    this.educationType = 'none',
    this.ageOver50 = false,
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
    // Deductions
    double? mortgageInterest,
    double? saltPaid,
    double? charitableContributions,
    double? medicalExpenses,
    // Retirement & Pre-tax
    double? contributions401k,
    double? iraContributions,
    double? hsaContributions,
    double? studentLoanInterest,
    // Family & Education
    int? numChildrenUnder17,
    int? numOtherDependents,
    double? educationExpenses,
    String? educationType,
    bool? ageOver50,
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
      // Deductions
      mortgageInterest: mortgageInterest ?? this.mortgageInterest,
      saltPaid: saltPaid ?? this.saltPaid,
      charitableContributions:
          charitableContributions ?? this.charitableContributions,
      medicalExpenses: medicalExpenses ?? this.medicalExpenses,
      // Retirement & Pre-tax
      contributions401k: contributions401k ?? this.contributions401k,
      iraContributions: iraContributions ?? this.iraContributions,
      hsaContributions: hsaContributions ?? this.hsaContributions,
      studentLoanInterest: studentLoanInterest ?? this.studentLoanInterest,
      // Family & Education
      numChildrenUnder17: numChildrenUnder17 ?? this.numChildrenUnder17,
      numOtherDependents: numOtherDependents ?? this.numOtherDependents,
      educationExpenses: educationExpenses ?? this.educationExpenses,
      educationType: educationType ?? this.educationType,
      ageOver50: ageOver50 ?? this.ageOver50,
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
        // Deductions
        mortgageInterest: mortgageInterest,
        saltPaid: saltPaid,
        charitableContributions: charitableContributions,
        medicalExpenses: medicalExpenses,
        // Retirement & Pre-tax
        contributions401k: contributions401k,
        iraContributions: iraContributions,
        hsaContributions: hsaContributions,
        studentLoanInterest: studentLoanInterest,
        // Family & Education
        numChildrenUnder17: numChildrenUnder17,
        numOtherDependents: numOtherDependents,
        educationExpenses: educationExpenses,
        educationType: educationType,
        ageOver50: ageOver50,
      );

  double get totalIncome =>
      wages + rsuIncome + capitalGainsShort + capitalGainsLong;

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
        // Deductions
        'mortgage_interest': mortgageInterest,
        'salt_paid': saltPaid,
        'charitable_contributions': charitableContributions,
        'medical_expenses': medicalExpenses,
        // Retirement & Pre-tax
        'contributions_401k': contributions401k,
        'ira_contributions': iraContributions,
        'hsa_contributions': hsaContributions,
        'student_loan_interest': studentLoanInterest,
        // Family & Education
        'num_children_under_17': numChildrenUnder17,
        'num_other_dependents': numOtherDependents,
        'education_expenses': educationExpenses,
        'education_type': educationType,
        'age_over_50': ageOver50,
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
      // Deductions
      mortgageInterest: (row['mortgage_interest'] as num?)?.toDouble() ?? 0,
      saltPaid: (row['salt_paid'] as num?)?.toDouble() ?? 0,
      charitableContributions:
          (row['charitable_contributions'] as num?)?.toDouble() ?? 0,
      medicalExpenses: (row['medical_expenses'] as num?)?.toDouble() ?? 0,
      // Retirement & Pre-tax
      contributions401k: (row['contributions_401k'] as num?)?.toDouble() ?? 0,
      iraContributions: (row['ira_contributions'] as num?)?.toDouble() ?? 0,
      hsaContributions: (row['hsa_contributions'] as num?)?.toDouble() ?? 0,
      studentLoanInterest:
          (row['student_loan_interest'] as num?)?.toDouble() ?? 0,
      // Family & Education
      numChildrenUnder17: (row['num_children_under_17'] as num?)?.toInt() ?? 0,
      numOtherDependents: (row['num_other_dependents'] as num?)?.toInt() ?? 0,
      educationExpenses: (row['education_expenses'] as num?)?.toDouble() ?? 0,
      educationType: row['education_type'] as String? ?? 'none',
      ageOver50: row['age_over_50'] as bool? ?? false,
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
      // Deductions
      mortgageInterest: prefs.getDouble('mortgageInterest') ?? 0,
      saltPaid: prefs.getDouble('saltPaid') ?? 0,
      charitableContributions:
          prefs.getDouble('charitableContributions') ?? 0,
      medicalExpenses: prefs.getDouble('medicalExpenses') ?? 0,
      // Retirement & Pre-tax
      contributions401k: prefs.getDouble('contributions401k') ?? 0,
      iraContributions: prefs.getDouble('iraContributions') ?? 0,
      hsaContributions: prefs.getDouble('hsaContributions') ?? 0,
      studentLoanInterest: prefs.getDouble('studentLoanInterest') ?? 0,
      // Family & Education
      numChildrenUnder17: prefs.getInt('numChildrenUnder17') ?? 0,
      numOtherDependents: prefs.getInt('numOtherDependents') ?? 0,
      educationExpenses: prefs.getDouble('educationExpenses') ?? 0,
      educationType: prefs.getString('educationType') ?? 'none',
      ageOver50: prefs.getBool('ageOver50') ?? false,
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
    // Deductions
    await prefs.setDouble('mortgageInterest', state.mortgageInterest);
    await prefs.setDouble('saltPaid', state.saltPaid);
    await prefs.setDouble(
        'charitableContributions', state.charitableContributions);
    await prefs.setDouble('medicalExpenses', state.medicalExpenses);
    // Retirement & Pre-tax
    await prefs.setDouble('contributions401k', state.contributions401k);
    await prefs.setDouble('iraContributions', state.iraContributions);
    await prefs.setDouble('hsaContributions', state.hsaContributions);
    await prefs.setDouble('studentLoanInterest', state.studentLoanInterest);
    // Family & Education
    await prefs.setInt('numChildrenUnder17', state.numChildrenUnder17);
    await prefs.setInt('numOtherDependents', state.numOtherDependents);
    await prefs.setDouble('educationExpenses', state.educationExpenses);
    await prefs.setString('educationType', state.educationType);
    await prefs.setBool('ageOver50', state.ageOver50);
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

  // Deduction setters
  void setMortgageInterest(double v) {
    state = state.copyWith(mortgageInterest: v);
    _persist();
  }

  void setSaltPaid(double v) {
    state = state.copyWith(saltPaid: v);
    _persist();
  }

  void setCharitableContributions(double v) {
    state = state.copyWith(charitableContributions: v);
    _persist();
  }

  void setMedicalExpenses(double v) {
    state = state.copyWith(medicalExpenses: v);
    _persist();
  }

  // Retirement & Pre-tax setters
  void setContributions401k(double v) {
    state = state.copyWith(contributions401k: v);
    _persist();
  }

  void setIraContributions(double v) {
    state = state.copyWith(iraContributions: v);
    _persist();
  }

  void setHsaContributions(double v) {
    state = state.copyWith(hsaContributions: v);
    _persist();
  }

  void setStudentLoanInterest(double v) {
    state = state.copyWith(studentLoanInterest: v);
    _persist();
  }

  // Family & Education setters
  void setNumChildrenUnder17(int v) {
    state = state.copyWith(numChildrenUnder17: v);
    _persist();
  }

  void setNumOtherDependents(int v) {
    state = state.copyWith(numOtherDependents: v);
    _persist();
  }

  void setEducationExpenses(double v) {
    state = state.copyWith(educationExpenses: v);
    _persist();
  }

  void setEducationType(String v) {
    state = state.copyWith(educationType: v);
    _persist();
  }

  void setAgeOver50(bool v) {
    state = state.copyWith(ageOver50: v);
    _persist();
  }
}
