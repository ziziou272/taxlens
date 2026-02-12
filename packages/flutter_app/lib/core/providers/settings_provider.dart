import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';

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
}

final settingsProvider =
    StateNotifierProvider<SettingsNotifier, UserSettings>((ref) {
  return SettingsNotifier();
});

class SettingsNotifier extends StateNotifier<UserSettings> {
  SettingsNotifier() : super(const UserSettings());

  void update(UserSettings Function(UserSettings) updater) {
    state = updater(state);
  }

  void setFilingStatus(String v) => state = state.copyWith(filingStatus: v);
  void setState(String v) => state = state.copyWith(state: v);
  void setWages(double v) => state = state.copyWith(wages: v);
  void setRsuIncome(double v) => state = state.copyWith(rsuIncome: v);
  void setCapitalGainsShort(double v) =>
      state = state.copyWith(capitalGainsShort: v);
  void setCapitalGainsLong(double v) =>
      state = state.copyWith(capitalGainsLong: v);
  void setFederalWithheld(double v) =>
      state = state.copyWith(federalWithheld: v);
  void setStateWithheld(double v) =>
      state = state.copyWith(stateWithheld: v);
  void setOnboardingComplete(bool v) =>
      state = state.copyWith(onboardingComplete: v);
}
