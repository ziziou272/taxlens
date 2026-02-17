import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import 'tax_returns_provider.dart';
import 'tax_return_model.dart';

class TaxReturnDetailScreen extends ConsumerWidget {
  const TaxReturnDetailScreen({super.key, required this.taxYear});
  final int taxYear;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(taxReturnDetailProvider(taxYear));

    return Scaffold(
      appBar: AppBar(
        title: Text('$taxYear Tax Return'),
        actions: [
          detailAsync.whenOrNull(
            data: (tr) => tr != null
                ? IconButton(
                    icon: const Icon(Icons.delete_outline),
                    color: AppColors.negative,
                    tooltip: 'Delete',
                    onPressed: () => _confirmDelete(context, ref, tr),
                  )
                : null,
          ) ?? const SizedBox.shrink(),
        ],
      ),
      body: detailAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.error_outline, color: AppColors.negative, size: 48),
                const SizedBox(height: 16),
                Text('Failed to load return: $err',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppColors.textSecondary)),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: () => context.pop(),
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Go back'),
                ),
              ],
            ),
          ),
        ),
        data: (tr) {
          if (tr == null) {
            return const Center(child: Text('Return not found'));
          }
          return _TaxReturnDetail(taxReturn: tr);
        },
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
            'Remove the $taxYear tax return? This cannot be undone.'),
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
      await ref.read(taxReturnsProvider.notifier).deleteYear(taxYear);
      if (context.mounted) context.go('/tax-returns');
    }
  }
}

class _TaxReturnDetail extends StatelessWidget {
  const _TaxReturnDetail({required this.taxReturn});
  final TaxReturn taxReturn;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: r'$', decimalDigits: 0);
    final theme = Theme.of(context);

    final isRefund = (taxReturn.refundOrOwed ?? 0) >= 0;
    final refundColor = isRefund ? AppColors.positive : AppColors.negative;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${taxReturn.taxYear} Tax Return',
                            style: theme.textTheme.titleLarge!
                                .copyWith(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            taxReturn.filingStatusLabel,
                            style: TextStyle(color: AppColors.textSecondary),
                          ),
                        ],
                      ),
                      if (taxReturn.refundOrOwed != null)
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              isRefund ? 'REFUND' : 'OWED',
                              style: TextStyle(
                                color: refundColor,
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 1,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              fmt.format(taxReturn.refundOrOwed!.abs()),
                              style: theme.textTheme.headlineSmall!.copyWith(
                                color: refundColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                  if (taxReturn.extractionConfidence != null) ...[
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Icon(Icons.auto_awesome, size: 14,
                            color: AppColors.textSecondary),
                        const SizedBox(width: 6),
                        Text(
                          'AI-extracted · ${(taxReturn.extractionConfidence! * 100).round()}% confidence',
                          style: TextStyle(
                              color: AppColors.textSecondary, fontSize: 12),
                        ),
                        const Spacer(),
                        _SourceBadge(source: taxReturn.source),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Key metrics row
          Row(
            children: [
              Expanded(
                child: _MetricCard(
                  label: 'Adjusted Gross\nIncome',
                  value: taxReturn.adjustedGrossIncome != null
                      ? fmt.format(taxReturn.adjustedGrossIncome!)
                      : '—',
                  color: AppColors.brand,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _MetricCard(
                  label: 'Total Tax',
                  value: taxReturn.totalTax != null
                      ? fmt.format(taxReturn.totalTax!)
                      : '—',
                  color: AppColors.warning,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _MetricCard(
                  label: 'Effective\nRate',
                  value: taxReturn.effectiveTaxRateLabel,
                  color: AppColors.info,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Detail breakdown
          Text('Income & Deductions',
              style: theme.textTheme.titleMedium),
          const SizedBox(height: 12),
          _DetailsCard(
            rows: [
              _DetailRow('Total Income',
                  taxReturn.totalIncome != null ? fmt.format(taxReturn.totalIncome!) : '—'),
              _DetailRow('Adjusted Gross Income',
                  taxReturn.adjustedGrossIncome != null ? fmt.format(taxReturn.adjustedGrossIncome!) : '—'),
              _DetailRow(
                'Deduction Type',
                taxReturn.deductionType != null
                    ? (taxReturn.deductionType == 'standard'
                        ? 'Standard Deduction'
                        : 'Itemized Deductions')
                    : '—',
              ),
              _DetailRow('Deduction Amount',
                  taxReturn.deductionAmount != null ? fmt.format(taxReturn.deductionAmount!) : '—'),
              _DetailRow('Taxable Income',
                  taxReturn.taxableIncome != null ? fmt.format(taxReturn.taxableIncome!) : '—'),
            ],
          ),
          const SizedBox(height: 16),

          Text('Tax Liability', style: theme.textTheme.titleMedium),
          const SizedBox(height: 12),
          _DetailsCard(
            rows: [
              _DetailRow('Total Tax',
                  taxReturn.totalTax != null ? fmt.format(taxReturn.totalTax!) : '—'),
              _DetailRow('Total Credits',
                  taxReturn.totalCredits != null ? fmt.format(taxReturn.totalCredits!) : '—'),
              _DetailRow('Federal Tax Withheld',
                  taxReturn.federalWithheld != null ? fmt.format(taxReturn.federalWithheld!) : '—'),
              _DetailRow(
                isRefund ? 'Refund Amount' : 'Amount Owed',
                taxReturn.refundOrOwed != null
                    ? fmt.format(taxReturn.refundOrOwed!.abs())
                    : '—',
                color: refundColor,
              ),
            ],
          ),

          if (taxReturn.scheduleData != null &&
              taxReturn.scheduleData!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text('Schedules', style: theme.textTheme.titleMedium),
            const SizedBox(height: 12),
            _DetailsCard(
              rows: taxReturn.scheduleData!.entries
                  .map((e) => _DetailRow(e.key, e.value.toString()))
                  .toList(),
            ),
          ],

          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 11,
                height: 1.3),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailsCard extends StatelessWidget {
  const _DetailsCard({required this.rows});
  final List<_DetailRow> rows;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: rows.asMap().entries.map((entry) {
          final i = entry.key;
          final row = entry.value;
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(row.label,
                        style: TextStyle(
                            color: AppColors.textSecondary, fontSize: 14)),
                    Text(
                      row.value,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: row.color ?? AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
              if (i < rows.length - 1)
                Divider(
                    height: 1,
                    color: AppColors.textSecondary.withAlpha(40)),
            ],
          );
        }).toList(),
      ),
    );
  }
}

class _DetailRow {
  const _DetailRow(this.label, this.value, {this.color});
  final String label;
  final String value;
  final Color? color;
}

class _SourceBadge extends StatelessWidget {
  const _SourceBadge({required this.source});
  final String source;

  @override
  Widget build(BuildContext context) {
    String label;
    Color color;
    switch (source) {
      case 'pdf_upload':
        label = 'PDF Import';
        color = AppColors.brand;
        break;
      case 'manual':
        label = 'Manual Entry';
        color = AppColors.info;
        break;
      case 'irs_transcript':
        label = 'IRS Transcript';
        color = AppColors.positive;
        break;
      default:
        label = source;
        color = AppColors.textSecondary;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withAlpha(30),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withAlpha(80)),
      ),
      child: Text(
        label,
        style: TextStyle(
            color: color, fontSize: 11, fontWeight: FontWeight.w600),
      ),
    );
  }
}
