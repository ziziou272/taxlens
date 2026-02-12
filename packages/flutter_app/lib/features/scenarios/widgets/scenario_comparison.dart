import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/models/scenario.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_theme.dart';

class ScenarioComparison extends StatelessWidget {
  const ScenarioComparison({super.key, required this.scenario});
  final Scenario scenario;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(scenario.name,
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _TaxColumn(
                    label: 'Current', amount: fmt.format(scenario.currentTax)),
                const Icon(Icons.arrow_forward, color: AppColors.textSecondary),
                _TaxColumn(
                    label: 'Projected',
                    amount: fmt.format(scenario.projectedTax)),
              ],
            ),
            const Divider(height: 24),
            Row(
              children: [
                const Icon(Icons.savings, color: AppColors.positive, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Save ${fmt.format(scenario.savings)}',
                  style: AppTheme.mono.copyWith(
                      color: AppColors.positive,
                      fontWeight: FontWeight.bold,
                      fontSize: 16),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _TaxColumn extends StatelessWidget {
  const _TaxColumn({required this.label, required this.amount});
  final String label;
  final String amount;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(amount,
            style: AppTheme.mono
                .copyWith(fontSize: 18, fontWeight: FontWeight.w600)),
      ],
    );
  }
}
