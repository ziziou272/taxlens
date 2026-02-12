import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import 'equity_provider.dart';
import 'widgets/holding_card.dart';

class EquityScreen extends ConsumerWidget {
  const EquityScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final holdings = ref.watch(holdingsProvider);
    final fmt = NumberFormat.currency(symbol: '\$');

    final totalValue =
        holdings.fold<double>(0, (s, h) => s + h.currentValue);
    final totalCost = holdings.fold<double>(0, (s, h) => s + h.costBasis);
    final totalGain = totalValue - totalCost;

    final grouped = <GrantType, List<Holding>>{};
    for (final h in holdings) {
      grouped.putIfAbsent(h.grantType, () => []).add(h);
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Equity Portfolio')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text('Total Portfolio Value',
                      style: TextStyle(color: AppColors.textSecondary)),
                  const SizedBox(height: 4),
                  Text(fmt.format(totalValue),
                      style: Theme.of(context).textTheme.headlineMedium),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _SummaryItem(
                          label: 'Cost Basis', value: fmt.format(totalCost)),
                      _SummaryItem(
                        label: 'Unrealized Gain',
                        value: fmt.format(totalGain),
                        color: totalGain >= 0
                            ? AppColors.positive
                            : AppColors.negative,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          for (final entry in grouped.entries) ...[
            Padding(
              padding: const EdgeInsets.only(top: 8, bottom: 8),
              child: Text(
                entry.value.first.grantTypeLabel,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
            ),
            for (final holding in entry.value)
              HoldingCard(
                holding: holding,
                onTap: () => context.push('/equity/${holding.id}'),
              ),
          ],
        ],
      ),
    );
  }
}

class _SummaryItem extends StatelessWidget {
  const _SummaryItem({required this.label, required this.value, this.color});
  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label,
            style:
                TextStyle(color: AppColors.textSecondary, fontSize: 12)),
        const SizedBox(height: 4),
        Text(value,
            style: TextStyle(
                color: color, fontWeight: FontWeight.bold, fontSize: 16)),
      ],
    );
  }
}
