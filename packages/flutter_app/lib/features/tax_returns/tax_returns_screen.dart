import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import 'tax_returns_provider.dart';
import 'tax_return_model.dart';

class TaxReturnsScreen extends ConsumerWidget {
  const TaxReturnsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final returnsAsync = ref.watch(taxReturnsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Prior Year Returns'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () => ref.read(taxReturnsProvider.notifier).refresh(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/tax-returns/upload'),
        icon: const Icon(Icons.upload_file),
        label: const Text('Import Year'),
      ),
      body: returnsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => _ErrorState(
          message: err.toString(),
          onRetry: () => ref.read(taxReturnsProvider.notifier).refresh(),
        ),
        data: (returns) => returns.isEmpty
            ? _EmptyState(
                onImport: () => context.push('/tax-returns/upload'),
              )
            : _ReturnsList(returns: returns),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.onImport});
  final VoidCallback onImport;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.receipt_long_outlined,
              size: 72,
              color: AppColors.brand.withAlpha(180),
            ),
            const SizedBox(height: 24),
            Text(
              'No Prior Year Returns',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            Text(
              'Import your previous 1040 tax returns to unlock year-over-year comparisons and AI tax insights.',
              style: TextStyle(color: AppColors.textSecondary, height: 1.5),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: onImport,
              icon: const Icon(Icons.upload_file),
              label: const Text('Import a Tax Return'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 14,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 48, color: AppColors.negative),
            const SizedBox(height: 16),
            Text(
              'Failed to load returns',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: TextStyle(color: AppColors.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            OutlinedButton.icon(
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

class _ReturnsList extends ConsumerWidget {
  const _ReturnsList({required this.returns});
  final List<TaxReturn> returns;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      itemCount: returns.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, i) => _TaxReturnCard(
        taxReturn: returns[i],
        onTap: () => context.push('/tax-returns/${returns[i].taxYear}'),
        onDelete: () => _confirmDelete(context, ref, returns[i]),
      ),
    );
  }

  Future<void> _confirmDelete(
      BuildContext context, WidgetRef ref, TaxReturn tr) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Return?'),
        content: Text(
          'Remove the ${tr.taxYear} tax return? This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppColors.negative),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed == true && context.mounted) {
      await ref.read(taxReturnsProvider.notifier).deleteYear(tr.taxYear);
    }
  }
}

class _TaxReturnCard extends StatelessWidget {
  const _TaxReturnCard({
    required this.taxReturn,
    required this.onTap,
    required this.onDelete,
  });

  final TaxReturn taxReturn;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: r'$', decimalDigits: 0);
    final theme = Theme.of(context);

    final isRefund = (taxReturn.refundOrOwed ?? 0) >= 0;
    final refundColor = isRefund ? AppColors.positive : AppColors.negative;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.brand.withAlpha(40),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${taxReturn.taxYear}',
                      style: theme.textTheme.titleLarge!.copyWith(
                        color: AppColors.brand,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          taxReturn.filingStatusLabel,
                          style: theme.textTheme.bodyMedium,
                        ),
                        if (taxReturn.adjustedGrossIncome != null)
                          Text(
                            'AGI: ${fmt.format(taxReturn.adjustedGrossIncome!)}',
                            style: TextStyle(
                                color: AppColors.textSecondary, fontSize: 13),
                          ),
                      ],
                    ),
                  ),
                  if (taxReturn.refundOrOwed != null)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: refundColor.withAlpha(30),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: refundColor.withAlpha(80)),
                      ),
                      child: Text(
                        isRefund
                            ? '+${fmt.format(taxReturn.refundOrOwed!)}'
                            : '-${fmt.format(taxReturn.refundOrOwed!.abs())}',
                        style: TextStyle(
                          color: refundColor,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ),
                ],
              ),
              if (taxReturn.totalTax != null ||
                  taxReturn.effectiveTaxRateLabel != '—') ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    _StatChip(
                      label: 'Total Tax',
                      value: taxReturn.totalTax != null
                          ? fmt.format(taxReturn.totalTax!)
                          : '—',
                    ),
                    const SizedBox(width: 8),
                    _StatChip(
                      label: 'Eff. Rate',
                      value: taxReturn.effectiveTaxRateLabel,
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.delete_outline, size: 20),
                      color: AppColors.textSecondary,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      onPressed: onDelete,
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  const _StatChip({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.cardDark,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label,
              style: const TextStyle(
                  fontSize: 10, color: AppColors.textSecondary)),
          Text(value,
              style: const TextStyle(
                  fontSize: 13, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
