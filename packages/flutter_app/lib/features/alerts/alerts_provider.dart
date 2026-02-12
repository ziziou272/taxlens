import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';
import '../../core/models/alert.dart';
import '../../core/providers/api_provider.dart';
import '../dashboard/dashboard_provider.dart';

/// Converts API alerts to the Alert model for display.
final alertsProvider = Provider<List<Alert>>((ref) {
  final result = ref.watch(alertsResultProvider);
  return result.when(
    data: (r) {
      if (r == null) return [];
      return r.alerts.asMap().entries.map((e) {
        final a = e.value;
        return Alert(
          id: '${e.key}',
          title: a.title,
          description: a.message,
          priority: _toPriority(a.severity),
        );
      }).toList();
    },
    loading: () => [],
    error: (_, __) => [],
  );
});

AlertPriority _toPriority(String severity) => switch (severity) {
      'critical' => AlertPriority.critical,
      'warning' => AlertPriority.warning,
      _ => AlertPriority.info,
    };

/// Provider for dismissing an alert.
final dismissAlertProvider =
    FutureProvider.family<void, String>((ref, alertId) async {
  final api = ref.read(apiClientProvider);
  await api.dismissAlert(alertId);
});
