import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_theme.dart';

class TaxSummaryCard extends StatelessWidget {
  const TaxSummaryCard({
    super.key,
    required this.totalTax,
    required this.effectiveRate,
    required this.marginalRate,
  });

  final double totalTax;
  final double effectiveRate;
  final double marginalRate;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Estimated Total Tax',
                style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            Text(
              fmt.format(totalTax),
              style: AppTheme.mono.copyWith(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppColors.negative,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _RateChip(label: 'Effective', value: effectiveRate),
                const SizedBox(width: 16),
                _RateChip(label: 'Marginal', value: marginalRate),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _RateChip extends StatelessWidget {
  const _RateChip({required this.label, required this.value});
  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text('${value.toStringAsFixed(1)}%',
            style: AppTheme.mono.copyWith(
                fontSize: 18, fontWeight: FontWeight.w600)),
      ],
    );
  }
}
