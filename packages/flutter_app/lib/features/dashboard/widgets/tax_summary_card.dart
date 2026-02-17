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
            Text('Your estimated tax this year',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: AppColors.textSecondary,
                    )),
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
                _RateChip(
                  label: 'Avg rate',
                  value: effectiveRate,
                  tooltip:
                      'Your total tax divided by total income.\nFor every \$100 you earn, you pay \$${(effectiveRate).toStringAsFixed(0)} in tax.',
                ),
                const SizedBox(width: 16),
                _RateChip(
                  label: 'Top rate',
                  value: marginalRate,
                  tooltip:
                      'The tax rate on your next dollar of income.\nNot all your income is taxed at this rate — only the portion in the top bracket.',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _RateChip extends StatelessWidget {
  const _RateChip({
    required this.label,
    required this.value,
    this.tooltip,
  });
  final String label;
  final double value;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall),
            if (tooltip != null) ...[
              const SizedBox(width: 4),
              Tooltip(
                message: tooltip!,
                triggerMode: TooltipTriggerMode.tap,
                showDuration: const Duration(seconds: 5),
                preferBelow: true,
                child: Icon(Icons.info_outline,
                    size: 14, color: AppColors.textSecondary),
              ),
            ],
          ],
        ),
        Text('${value.toStringAsFixed(1)}%',
            style: AppTheme.mono
                .copyWith(fontSize: 18, fontWeight: FontWeight.w600)),
      ],
    );
    return content;
  }
}
