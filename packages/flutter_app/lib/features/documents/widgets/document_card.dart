import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../documents_provider.dart';

class DocumentCard extends StatelessWidget {
  const DocumentCard({super.key, required this.document, this.onTap});
  final TaxDocument document;
  final VoidCallback? onTap;

  IconData get _typeIcon => switch (document.type) {
        DocumentType.w2 => Icons.work_outline,
        DocumentType.form1099B => Icons.trending_up,
        DocumentType.form1099DIV => Icons.account_balance,
        DocumentType.form3922 => Icons.receipt_long,
      };

  Color get _statusColor => switch (document.status) {
        DocumentStatus.processing => AppColors.warning,
        DocumentStatus.reviewNeeded => AppColors.info,
        DocumentStatus.confirmed => AppColors.positive,
      };

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(
          backgroundColor: AppColors.brand.withAlpha(30),
          child: Icon(_typeIcon, color: AppColors.brand),
        ),
        title: Text(document.typeLabel),
        subtitle: Text(
          '${document.fileName} • ${DateFormat.yMMMd().format(document.uploadDate)}',
          style: const TextStyle(fontSize: 12),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _statusColor.withAlpha(30),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            document.statusLabel,
            style: TextStyle(color: _statusColor, fontSize: 11),
          ),
        ),
      ),
    );
  }
}
