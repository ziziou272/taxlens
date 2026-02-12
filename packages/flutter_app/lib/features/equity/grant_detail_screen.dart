import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import 'equity_provider.dart';
import 'widgets/tax_lot_row.dart';
import 'widgets/holding_period_badge.dart';

class GrantDetailScreen extends ConsumerWidget {
  const GrantDetailScreen({super.key, required this.grantId});
  final String grantId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final holding = ref.watch(grantDetailProvider(grantId));
    final fmt = NumberFormat.currency(symbol: '\$');
    final dateFmt = DateFormat.yMMMd();

    if (holding == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Grant Detail')),
        body: const Center(child: Text('Grant not found')),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('${holding.symbol} ${holding.grantTypeLabel}')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Grant info card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Grant Information',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  _InfoRow('Type', holding.grantTypeLabel),
                  if (holding.grantDate != null)
                    _InfoRow('Grant Date', dateFmt.format(holding.grantDate!)),
                  if (holding.sharesGranted != null)
                    _InfoRow('Shares Granted', '${holding.sharesGranted}'),
                  if (holding.sharesVested != null)
                    _InfoRow('Shares Vested', '${holding.sharesVested}'),
                  if (holding.exercisePrice != null)
                    _InfoRow('Exercise Price', fmt.format(holding.exercisePrice)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Vesting progress
          if (holding.sharesGranted != null && holding.sharesVested != null)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Vesting Progress',
                        style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 12),
                    LinearProgressIndicator(
                      value: holding.sharesVested! / holding.sharesGranted!,
                      minHeight: 8,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${holding.sharesVested} / ${holding.sharesGranted} shares vested',
                      style: TextStyle(
                          color: AppColors.textSecondary, fontSize: 13),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 12),

          // Tax lots
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Tax Lots',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  for (final lot in holding.taxLots) ...[
                    TaxLotRow(lot: lot),
                    if (lot != holding.taxLots.last) const Divider(),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Holding period badges
          Wrap(
            spacing: 8,
            children: [
              for (final lot in holding.taxLots)
                HoldingPeriodBadge(lot: lot),
            ],
          ),
          const SizedBox(height: 24),

          FilledButton.icon(
            onPressed: () => context.push('/scenarios'),
            icon: const Icon(Icons.calculate),
            label: const Text('What-if: Sell Now'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.all(16),
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow(this.label, this.value);
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
