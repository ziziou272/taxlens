import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';
import '../../core/models/scenario.dart';
import '../../core/providers/api_provider.dart';
import '../../core/providers/settings_provider.dart';

/// Fetches available scenario types from the API.
final scenarioTypesProvider =
    FutureProvider<List<ScenarioType>>((ref) async {
  final api = ref.read(apiClientProvider);
  return api.getScenarioTypes();
});

/// Runs a scenario comparison.
final scenarioResultProvider = AsyncNotifierProvider<ScenarioResultNotifier,
    ScenarioComparison?>(ScenarioResultNotifier.new);

class ScenarioResultNotifier extends AsyncNotifier<ScenarioComparison?> {
  @override
  Future<ScenarioComparison?> build() async => null;

  Future<void> runComparison({
    required String scenarioType,
    required Map<String, dynamic> alternativeOverrides,
  }) async {
    state = const AsyncValue.loading();
    final api = ref.read(apiClientProvider);
    final settings = ref.read(settingsProvider);

    final baseInput = {
      'name': 'Current',
      'scenario_type': scenarioType,
      'filing_status': settings.filingStatus,
      'wages': settings.wages,
      'rsu_income': settings.rsuIncome,
      'short_term_gains': settings.capitalGainsShort,
      'long_term_gains': settings.capitalGainsLong,
      'state': settings.state,
    };

    final altInput = {...baseInput, 'name': 'Alternative', ...alternativeOverrides};

    state = await AsyncValue.guard(() async {
      return api.runScenario(
        ScenarioRunInput(baseline: baseInput, alternative: altInput),
      );
    });
  }
}

/// Legacy provider for backward compatibility — provides static list.
final scenariosProvider = Provider<List<Scenario>>((ref) {
  final result = ref.watch(scenarioResultProvider);
  return result.when(
    data: (comparison) {
      if (comparison == null) return [];
      return [
        Scenario(
          id: '1',
          name: comparison.alternative.name,
          type: 'custom',
          currentTax: comparison.baseline.totalTax,
          projectedTax: comparison.alternative.totalTax,
          savings: comparison.taxSavings,
        ),
      ];
    },
    loading: () => [],
    error: (_, __) => [],
  );
});
