import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import 'documents_provider.dart';
import 'widgets/extracted_data_view.dart';

class DocumentDetailScreen extends ConsumerWidget {
  const DocumentDetailScreen({super.key, required this.documentId});
  final String documentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final doc = ref.watch(documentDetailProvider(documentId));

    if (doc == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Document')),
        body: const Center(child: Text('Document not found')),
      );
    }

    final statusColor = switch (doc.status) {
      DocumentStatus.processing => AppColors.warning,
      DocumentStatus.reviewNeeded => AppColors.info,
      DocumentStatus.confirmed => AppColors.positive,
    };

    return Scaffold(
      appBar: AppBar(title: Text(doc.typeLabel)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.description, size: 40, color: AppColors.brand),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(doc.fileName,
                              style: Theme.of(context).textTheme.titleMedium),
                          const SizedBox(height: 4),
                          Text(
                            'Uploaded ${DateFormat.yMMMd().format(doc.uploadDate)}',
                            style: TextStyle(color: AppColors.textSecondary),
                          ),
                        ],
                      ),
                    ),
                    Chip(
                      label: Text(doc.statusLabel,
                          style: const TextStyle(fontSize: 12)),
                      backgroundColor: statusColor.withAlpha(40),
                      side: BorderSide(color: statusColor.withAlpha(80)),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (doc.status == DocumentStatus.processing)
              const Center(
                child: Column(
                  children: [
                    SizedBox(height: 40),
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Extracting data from document...'),
                  ],
                ),
              )
            else if (doc.extractedData != null) ...[
              Text('Extracted Data',
                  style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 12),
              ExtractedDataView(
                data: doc.extractedData!,
                onSave: (updated) {
                  ref
                      .read(documentsProvider.notifier)
                      .updateExtractedData(doc.id, updated);
                },
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.refresh),
                      label: const Text('Re-extract'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: doc.status == DocumentStatus.confirmed
                          ? null
                          : () {
                              ref
                                  .read(documentsProvider.notifier)
                                  .confirmDocument(doc.id);
                            },
                      icon: const Icon(Icons.check),
                      label: Text(doc.status == DocumentStatus.confirmed
                          ? 'Confirmed'
                          : 'Confirm'),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
