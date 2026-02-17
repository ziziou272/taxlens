import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/models/tax_result.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_theme.dart';

class TaxSummaryCard extends StatelessWidget {
  const TaxSummaryCard({
    super.key,
    required this.totalTax,
    required this.effectiveRate,
    required this.marginalRate,
    this.result,
  });

  final double totalTax;
  final double effectiveRate;
  final double marginalRate;

  /// Full result object for optional extra detail rows.
  final TaxResult? result;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    final r = result;

    final hasCredits = r != null &&
        (r.childTaxCredit > 0 ||
            r.otherDependentCredit > 0 ||
            r.actc > 0 ||
            r.eitc > 0 ||
            r.educationCredit > 0 ||
            r.educationCreditRefundable > 0 ||
            r.totalCredits > 0);

    final hasAboveTheLine =
        r != null && r.aboveTheLineDeductionsTotal > 0;

    final hasItemized = r != null && r.itemizedDeductionsTotal > 0;
    final usedItemized =
        hasItemized && r.itemizedDeductionsTotal > r.deductionUsed;

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

            // ── AGI & deduction info ────────────────────────────────────────
            if (r != null && r.agi > 0) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              _DetailRow(
                label: 'Adjusted Gross Income (AGI)',
                value: fmt.format(r.agi),
                tooltip:
                    'Your income after above-the-line deductions. Used to calculate many credits and phase-outs.',
              ),
            ],

            if (hasAboveTheLine) ...[
              const SizedBox(height: 4),
              _DetailRow(
                label: 'Above-the-line deductions',
                value: '− ${fmt.format(r!.aboveTheLineDeductionsTotal)}',
                valueColor: AppColors.positive,
                tooltip:
                    'Includes 401(k), IRA, HSA, student loan interest, and other pre-tax deductions.',
              ),
            ],

            if (r != null && r.deductionUsed > 0) ...[
              const SizedBox(height: 4),
              _DetailRow(
                label: usedItemized
                    ? 'Itemized deduction used'
                    : 'Standard deduction used',
                value: '− ${fmt.format(r.deductionUsed)}',
                valueColor: AppColors.positive,
                tooltip: usedItemized
                    ? 'Your itemized deductions (mortgage, SALT, charity, medical) exceeded the standard deduction.'
                    : 'The standard deduction was larger than your itemized deductions.',
              ),
              if (hasItemized && !usedItemized) ...[
                const SizedBox(height: 2),
                Text(
                  'Your itemized total (${fmt.format(r.itemizedDeductionsTotal)}) is less than the standard deduction.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                        fontStyle: FontStyle.italic,
                      ),
                ),
              ],
            ],

            // ── Credits breakdown ───────────────────────────────────────────
            if (hasCredits) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              Text(
                'Tax credits applied',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
              const SizedBox(height: 8),
              if (r!.childTaxCredit > 0)
                _CreditRow(
                  label: 'Child Tax Credit',
                  value: r.childTaxCredit,
                  fmt: fmt,
                  tooltip:
                      'Up to \$2,000 per qualifying child under 17.',
                ),
              if (r.actc > 0)
                _CreditRow(
                  label: 'Additional Child Tax Credit (refundable)',
                  value: r.actc,
                  fmt: fmt,
                  tooltip:
                      'The refundable portion of the child tax credit — you get this back even if you owe no tax.',
                ),
              if (r.otherDependentCredit > 0)
                _CreditRow(
                  label: 'Other Dependent Credit',
                  value: r.otherDependentCredit,
                  fmt: fmt,
                  tooltip:
                      '\$500 non-refundable credit for each qualifying dependent who is not a child under 17.',
                ),
              if (r.eitc > 0)
                _CreditRow(
                  label: 'Earned Income Tax Credit (EITC)',
                  value: r.eitc,
                  fmt: fmt,
                  tooltip:
                      'A refundable credit for low-to-moderate income workers and families.',
                ),
              if (r.educationCredit > 0)
                _CreditRow(
                  label: 'Education Credit (non-refundable)',
                  value: r.educationCredit,
                  fmt: fmt,
                  tooltip:
                      'AOTC or LLC non-refundable portion — reduces your tax bill.',
                ),
              if (r.educationCreditRefundable > 0)
                _CreditRow(
                  label: 'Education Credit (refundable)',
                  value: r.educationCreditRefundable,
                  fmt: fmt,
                  tooltip:
                      '40% of the AOTC is refundable — you receive this even with no tax owed.',
                ),
              if (r.totalCredits > 0) ...[
                const SizedBox(height: 4),
                const Divider(indent: 0, endIndent: 0),
                _DetailRow(
                  label: 'Total credits',
                  value: '− ${fmt.format(r.totalCredits)}',
                  valueColor: AppColors.positive,
                  bold: true,
                  tooltip: 'Total tax credits reduce your final tax bill.',
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}

// ─── Helper widgets ───────────────────────────────────────────────────────────

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
    return Column(
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
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({
    required this.label,
    required this.value,
    this.valueColor,
    this.bold = false,
    this.tooltip,
  });

  final String label;
  final String value;
  final Color? valueColor;
  final bool bold;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          if (tooltip != null) ...[
            Tooltip(
              message: tooltip!,
              triggerMode: TooltipTriggerMode.tap,
              showDuration: const Duration(seconds: 5),
              child: Icon(Icons.info_outline,
                  size: 14, color: AppColors.textSecondary),
            ),
            const SizedBox(width: 4),
          ],
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight:
                        bold ? FontWeight.w600 : FontWeight.normal,
                  ),
            ),
          ),
          Text(
            value,
            style: AppTheme.mono.copyWith(
              fontSize: 13,
              fontWeight: bold ? FontWeight.w600 : FontWeight.normal,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }
}

class _CreditRow extends StatelessWidget {
  const _CreditRow({
    required this.label,
    required this.value,
    required this.fmt,
    this.tooltip,
  });

  final String label;
  final double value;
  final NumberFormat fmt;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Icon(Icons.check_circle_outline,
              size: 14, color: AppColors.positive),
          const SizedBox(width: 6),
          Expanded(
            child: Row(
              children: [
                Flexible(
                  child: Text(
                    label,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
                if (tooltip != null) ...[
                  const SizedBox(width: 4),
                  Tooltip(
                    message: tooltip!,
                    triggerMode: TooltipTriggerMode.tap,
                    showDuration: const Duration(seconds: 5),
                    child: Icon(Icons.info_outline,
                        size: 13, color: AppColors.textSecondary),
                  ),
                ],
              ],
            ),
          ),
          Text(
            '− ${fmt.format(value)}',
            style: AppTheme.mono.copyWith(
              fontSize: 13,
              color: AppColors.positive,
            ),
          ),
        ],
      ),
    );
  }
}
