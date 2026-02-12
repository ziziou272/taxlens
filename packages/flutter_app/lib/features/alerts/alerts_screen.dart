import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'alerts_provider.dart';
import 'widgets/alert_card.dart';
import '../dashboard/dashboard_provider.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertsProvider);
    final alertsAsync = ref.watch(alertsResultProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Alerts')),
      body: alertsAsync.when(
        data: (_) {
          if (alerts.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle_outline,
                      size: 64, color: Colors.green),
                  SizedBox(height: 16),
                  Text('No alerts. Calculate your taxes first.'),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: alerts.length,
            itemBuilder: (_, i) => AlertCard(alert: alerts[i]),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 16),
              Text(error.toString()),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: () {
                  final result = ref.read(taxResultProvider).valueOrNull;
                  if (result != null) {
                    ref
                        .read(alertsResultProvider.notifier)
                        .checkAlerts(result);
                  }
                },
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
