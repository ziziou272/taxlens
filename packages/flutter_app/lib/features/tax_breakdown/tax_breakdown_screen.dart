import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_theme.dart';
import 'tax_breakdown_provider.dart';

class TaxBreakdownScreen extends ConsumerWidget {
  const TaxBreakdownScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lines = ref.watch(taxBreakdownProvider);
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);

    return Scaffold(
      appBar: AppBar(title: const Text('Tax Breakdown')),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: lines.length,
        separatorBuilder: (_, __) => const Divider(height: 1),
        itemBuilder: (_, i) {
          final line = lines[i];
          final amount = line['amount'] as double;
          final indent = line['indent'] as int;
          final isTotal = line['label'] == 'Total Tax' ||
              line['label'] == 'Amount Owed';

          return Padding(
            padding: EdgeInsets.only(left: indent * 24.0, top: 12, bottom: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  line['label'] as String,
                  style: isTotal
                      ? Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold)
                      : null,
                ),
                Text(
                  fmt.format(amount.abs()),
                  style: AppTheme.mono.copyWith(
                    fontSize: isTotal ? 18 : 14,
                    fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
                    color: amount < 0 ? AppColors.positive : AppColors.negative,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
