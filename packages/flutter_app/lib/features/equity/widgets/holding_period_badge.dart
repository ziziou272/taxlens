import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../equity_provider.dart';

class HoldingPeriodBadge extends StatelessWidget {
  const HoldingPeriodBadge({super.key, required this.lot});
  final TaxLot lot;

  @override
  Widget build(BuildContext context) {
    final String label;
    final Color color;

    if (lot.isLongTerm) {
      label = 'Long-term';
      color = AppColors.positive;
    } else if (lot.daysToLongTerm <= 90) {
      label = 'LTCG in ${lot.daysToLongTerm} days';
      color = AppColors.warning;
    } else {
      label = 'Short-term';
      color = AppColors.negative;
    }

    return Chip(
      label: Text(label, style: TextStyle(color: color, fontSize: 12)),
      backgroundColor: color.withAlpha(25),
      side: BorderSide(color: color.withAlpha(60)),
      visualDensity: VisualDensity.compact,
    );
  }
}
