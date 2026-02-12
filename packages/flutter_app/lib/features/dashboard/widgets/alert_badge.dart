import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class AlertBadge extends StatelessWidget {
  const AlertBadge({
    super.key,
    required this.criticalCount,
    required this.warningCount,
  });

  final int criticalCount;
  final int warningCount;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 16),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (criticalCount > 0)
            _Badge(count: criticalCount, color: AppColors.negative),
          if (warningCount > 0) ...[
            const SizedBox(width: 8),
            _Badge(count: warningCount, color: AppColors.warning),
          ],
        ],
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  const _Badge({required this.count, required this.color});
  final int count;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withAlpha(40),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(
        '$count',
        style: TextStyle(
            color: color, fontWeight: FontWeight.bold, fontSize: 12),
      ),
    );
  }
}
