import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_theme.dart';

class WithholdingGapBar extends StatelessWidget {
  const WithholdingGapBar({
    super.key,
    required this.withheld,
    required this.projected,
  });

  final double withheld;
  final double projected;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    final ratio = (withheld / projected).clamp(0.0, 1.0);
    final gap = projected - withheld;
    final isOwed = gap > 0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Tax paid so far vs. what you\'ll owe',
                style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 12),
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: ratio,
                minHeight: 24,
                backgroundColor: AppColors.negative.withAlpha(60),
                valueColor:
                    const AlwaysStoppedAnimation<Color>(AppColors.positive),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Paid: ${fmt.format(withheld)}',
                    style: AppTheme.mono
                        .copyWith(fontSize: 14, color: AppColors.positive)),
                Text(
                  isOwed
                      ? 'You\'ll owe: ${fmt.format(gap)}'
                      : 'Refund coming: ${fmt.format(-gap)}',
                  style: AppTheme.mono.copyWith(
                    fontSize: 14,
                    color: isOwed ? AppColors.negative : AppColors.positive,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
