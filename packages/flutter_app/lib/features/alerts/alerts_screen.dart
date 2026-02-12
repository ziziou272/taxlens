import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'alerts_provider.dart';
import 'widgets/alert_card.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Alerts')),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: alerts.length,
        itemBuilder: (_, i) => AlertCard(alert: alerts[i]),
      ),
    );
  }
}
