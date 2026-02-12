import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dashboard_provider.dart';
import 'widgets/tax_summary_card.dart';
import 'widgets/withholding_gap_bar.dart';
import 'widgets/income_breakdown_chart.dart';
import 'widgets/alert_badge.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final result = ref.watch(dashboardProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('TaxLens'),
        actions: const [AlertBadge(criticalCount: 2, warningCount: 3)],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TaxSummaryCard(
            totalTax: result.totalTax,
            effectiveRate: result.effectiveRate,
            marginalRate: result.marginalRate,
          ),
          const SizedBox(height: 16),
          WithholdingGapBar(
            withheld: result.totalWithheld,
            projected: result.totalTax,
          ),
          const SizedBox(height: 16),
          IncomeBreakdownChart(breakdown: result.incomeBreakdown),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Calculating... (mock)')),
          );
        },
        icon: const Icon(Icons.calculate),
        label: const Text('Calculate'),
      ),
    );
  }
}
