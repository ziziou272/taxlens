import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'alerts_provider.dart';
import 'widgets/alert_card.dart';
import '../dashboard/dashboard_provider.dart';
import '../../core/theme/app_colors.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertsProvider);
    final alertsAsync = ref.watch(alertsResultProvider);
    final taxResult = ref.watch(taxResultProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Tax Tips')),
      body: alertsAsync.when(
        data: (_) {
          if (alerts.isEmpty) {
            // If tax has been calculated but no alerts, show "all good"
            if (taxResult.hasValue && taxResult.value != null) {
              return _AllGoodView();
            }
            return _EmptyTipsView();
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
                    ref.read(alertsResultProvider.notifier).checkAlerts(result);
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

class _EmptyTipsView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.brand.withAlpha(25),
            ),
            child: const Icon(Icons.lightbulb_outline,
                size: 48, color: AppColors.brand),
          ),
          const SizedBox(height: 24),
          Text('Personalized tax tips',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  )),
          const SizedBox(height: 12),
          Text(
            'Once you enter your income details, we\'ll automatically find ways to save you money on taxes.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 32),
          // Example tips
          _ExampleTip(
            icon: Icons.account_balance_outlined,
            text: 'Your 401(k) has room — save more, pay less tax',
          ),
          _ExampleTip(
            icon: Icons.schedule_outlined,
            text: 'Defer some income to next year to lower your bracket',
          ),
          _ExampleTip(
            icon: Icons.warning_amber_outlined,
            text: 'Heads up: you might owe extra at tax time',
          ),
          const SizedBox(height: 32),
          FilledButton.icon(
            onPressed: () => context.go('/'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.brand,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
            icon: const Icon(Icons.calculate_outlined),
            label: const Text('Enter your income to get tips'),
          ),
        ],
      ),
    );
  }
}

class _ExampleTip extends StatelessWidget {
  const _ExampleTip({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.brand),
          const SizedBox(width: 12),
          Expanded(
            child: Text(text,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    )),
          ),
        ],
      ),
    );
  }
}

class _AllGoodView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.positive.withAlpha(25),
              ),
              child: const Icon(Icons.check_circle_outline,
                  size: 48, color: AppColors.positive),
            ),
            const SizedBox(height: 24),
            Text('Looking good!',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    )),
            const SizedBox(height: 12),
            Text(
              'We checked your tax situation and didn\'t find any issues or savings opportunities right now. We\'ll keep watching!',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
