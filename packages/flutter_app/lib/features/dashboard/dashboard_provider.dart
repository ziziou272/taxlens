import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';
import '../../core/models/tax_result.dart';
import '../../core/providers/api_provider.dart';
import '../../core/providers/settings_provider.dart';

final taxResultProvider =
    AsyncNotifierProvider<TaxResultNotifier, TaxResult?>(TaxResultNotifier.new);

class TaxResultNotifier extends AsyncNotifier<TaxResult?> {
  @override
  Future<TaxResult?> build() async {
    return null;
  }

  Future<void> calculate() async {
    state = const AsyncValue.loading();
    final api = ref.read(apiClientProvider);
    final settings = ref.read(settingsProvider);

    state = await AsyncValue.guard(() async {
      final result = await api.calculateTax(settings.toTaxInput());
      return TaxResult(
        totalIncome: result.totalIncome,
        federalTax: result.federalTax,
        stateTax: result.stateTax,
        totalTax: result.totalTax,
        effectiveRate: result.effectiveRate,
        marginalRate: result.marginalRate,
        totalWithheld: settings.federalWithheld + settings.stateWithheld,
        amountOwed: result.amountOwed,
        taxableIncome: result.taxableIncome,
        deductionUsed: result.deductionUsed,
        socialSecurityTax: result.socialSecurityTax,
        medicareTax: result.medicareTax,
        incomeBreakdown: {
          if (settings.wages > 0) 'W-2 Salary': settings.wages,
          if (settings.rsuIncome > 0) 'RSU Vesting': settings.rsuIncome,
          if (settings.capitalGainsLong > 0)
            'LT Capital Gains': settings.capitalGainsLong,
          if (settings.capitalGainsShort > 0)
            'ST Capital Gains': settings.capitalGainsShort,
        },
      );
    });
  }
}

class AlertSummary {
  final int critical;
  final int warning;
  final int info;
  const AlertSummary({this.critical = 0, this.warning = 0, this.info = 0});
}

final alertSummaryProvider = Provider<AlertSummary>((ref) {
  final alertsAsync = ref.watch(alertsResultProvider);
  return alertsAsync.when(
    data: (result) {
      if (result == null) return const AlertSummary();
      int critical = 0, warning = 0, info = 0;
      for (final a in result.alerts) {
        switch (a.severity) {
          case 'critical':
            critical++;
          case 'warning':
            warning++;
          default:
            info++;
        }
      }
      return AlertSummary(critical: critical, warning: warning, info: info);
    },
    loading: () => const AlertSummary(),
    error: (_, __) => const AlertSummary(),
  );
});

final alertsResultProvider =
    AsyncNotifierProvider<AlertsResultNotifier, AlertCheckResult?>(
        AlertsResultNotifier.new);

class AlertsResultNotifier extends AsyncNotifier<AlertCheckResult?> {
  @override
  Future<AlertCheckResult?> build() async => null;

  Future<void> checkAlerts(TaxResult taxResult) async {
    state = const AsyncValue.loading();
    final api = ref.read(apiClientProvider);
    final settings = ref.read(settingsProvider);

    state = await AsyncValue.guard(() async {
      return api.checkAlerts(AlertCheckInput(
        totalIncome: taxResult.totalIncome,
        totalTaxLiability: taxResult.totalTax,
        totalWithheld: taxResult.totalWithheld,
        longTermGains: settings.capitalGainsLong,
        shortTermGains: settings.capitalGainsShort,
        rsuIncome: settings.rsuIncome,
        filingStatus: settings.filingStatus,
        state: settings.state,
      ));
    });
  }
}
