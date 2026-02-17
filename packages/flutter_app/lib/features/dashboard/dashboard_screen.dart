import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/settings_provider.dart';
import 'dashboard_provider.dart';
import 'widgets/tax_summary_card.dart';
import 'widgets/withholding_gap_bar.dart';
import 'widgets/income_breakdown_chart.dart';
import 'widgets/alert_badge.dart';
import 'widgets/tax_input_form.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final resultAsync = ref.watch(taxResultProvider);
    final alertSummary = ref.watch(alertSummaryProvider);
    final settings = ref.watch(settingsProvider);

    // Auto-calculate if onboarding is complete and we have income but no result
    if (settings.onboardingComplete &&
        settings.totalIncome > 0 &&
        resultAsync.value == null &&
        !resultAsync.isLoading &&
        !resultAsync.hasError) {
      // Schedule after build
      Future.microtask(() => ref.read(taxResultProvider.notifier).calculate());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('TaxLens'),
        actions: [
          AlertBadge(
            criticalCount: alertSummary.critical,
            warningCount: alertSummary.warning,
          ),
        ],
      ),
      body: resultAsync.when(
        data: (result) {
          if (result == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.calculate_outlined,
                      size: 64, color: Theme.of(context).colorScheme.primary),
                  const SizedBox(height: 16),
                  Text('Enter your income to see your tax picture',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: () => _showInputForm(context),
                    icon: const Icon(Icons.edit),
                    label: const Text('Enter Income'),
                  ),
                ],
              ),
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              TaxSummaryCard(
                totalTax: result.totalTax,
                effectiveRate: result.effectiveRate,
                marginalRate: result.marginalRate,
                result: result,
              ),
              const SizedBox(height: 16),
              WithholdingGapBar(
                withheld: result.totalWithheld,
                projected: result.totalTax,
              ),
              const SizedBox(height: 16),
              if (result.incomeBreakdown.isNotEmpty)
                IncomeBreakdownChart(breakdown: result.incomeBreakdown),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorView(
          message: error.toString(),
          onRetry: () => ref.read(taxResultProvider.notifier).calculate(),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showInputForm(context),
        icon: const Icon(Icons.calculate),
        label: const Text('Calculate'),
      ),
    );
  }

  void _showInputForm(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => const FractionallySizedBox(
        heightFactor: 0.9,
        child: TaxInputForm(),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
