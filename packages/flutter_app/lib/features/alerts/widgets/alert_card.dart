import 'package:flutter/material.dart';
import '../../../core/models/alert.dart';
import '../../../core/theme/app_colors.dart';

class AlertCard extends StatelessWidget {
  const AlertCard({super.key, required this.alert});
  final Alert alert;

  Color get _borderColor => switch (alert.priority) {
        AlertPriority.critical => AppColors.negative,
        AlertPriority.warning => AppColors.warning,
        AlertPriority.info => AppColors.info,
      };

  IconData get _icon => switch (alert.priority) {
        AlertPriority.critical => Icons.error,
        AlertPriority.warning => Icons.warning,
        AlertPriority.info => Icons.info_outline,
      };

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: _borderColor, width: 2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(_icon, color: _borderColor, size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(alert.title,
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(alert.description,
                      style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
