import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';
import '../../core/theme/app_colors.dart';
import 'tax_returns_provider.dart';
import 'tax_return_model.dart';

class UploadPdfScreen extends ConsumerStatefulWidget {
  const UploadPdfScreen({super.key});

  @override
  ConsumerState<UploadPdfScreen> createState() => _UploadPdfScreenState();
}

class _UploadPdfScreenState extends ConsumerState<UploadPdfScreen> {
  PlatformFile? _pickedFile;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: false,
      withReadStream: false,
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() => _pickedFile = result.files.first);
    }
  }

  Future<void> _upload() async {
    final file = _pickedFile;
    if (file == null || file.path == null) return;

    final extraction = await ref
        .read(uploadPdfProvider.notifier)
        .upload(file.path!, file.name);

    if (!mounted) return;
    if (extraction != null) {
      context.push('/tax-returns/review', extra: extraction);
    }
  }

  @override
  Widget build(BuildContext context) {
    final uploadState = ref.watch(uploadPdfProvider);
    final isUploading = uploadState.status == UploadStatus.uploading;
    final hasError = uploadState.status == UploadStatus.error;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Import Tax Return')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Icon(
              Icons.picture_as_pdf_outlined,
              size: 56,
              color: AppColors.brand,
            ),
            const SizedBox(height: 16),
            Text(
              'Upload Your 1040',
              style: theme.textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'We\'ll use AI to extract all key fields from your tax return. You\'ll review everything before we save it.',
              style: TextStyle(color: AppColors.textSecondary, height: 1.5),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),

            // File picker area
            GestureDetector(
              onTap: isUploading ? null : _pickFile,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.all(28),
                decoration: BoxDecoration(
                  color: _pickedFile != null
                      ? AppColors.brand.withAlpha(20)
                      : AppColors.cardDark,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _pickedFile != null
                        ? AppColors.brand
                        : AppColors.textSecondary.withAlpha(80),
                    width: _pickedFile != null ? 2 : 1,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      _pickedFile != null
                          ? Icons.check_circle_outline
                          : Icons.upload_file,
                      size: 40,
                      color: _pickedFile != null
                          ? AppColors.brand
                          : AppColors.textSecondary,
                    ),
                    const SizedBox(height: 12),
                    if (_pickedFile != null) ...[
                      Text(
                        _pickedFile!.name,
                        style: theme.textTheme.bodyMedium!
                            .copyWith(color: AppColors.brand),
                        textAlign: TextAlign.center,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${(_pickedFile!.size / 1024).toStringAsFixed(1)} KB · Tap to change',
                        style: TextStyle(
                            color: AppColors.textSecondary, fontSize: 12),
                        textAlign: TextAlign.center,
                      ),
                    ] else ...[
                      Text(
                        'Tap to select PDF',
                        style: theme.textTheme.bodyMedium!
                            .copyWith(color: AppColors.textSecondary),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Form 1040, 1040-SR, or 1040-NR',
                        style: const TextStyle(
                            color: AppColors.textSecondary, fontSize: 12),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Error message
            if (hasError)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.negative.withAlpha(30),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.negative.withAlpha(80)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline,
                        color: AppColors.negative, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        uploadState.error ?? 'Upload failed. Please try again.',
                        style: TextStyle(
                            color: AppColors.negative, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),

            const Spacer(),

            // What we extract info
            _InfoCard(),

            const SizedBox(height: 24),

            // Upload button
            if (isUploading) ...[
              const SizedBox(height: 8),
              LinearProgressIndicator(
                backgroundColor: AppColors.cardDark,
                color: AppColors.brand,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 12),
              Text(
                'Extracting data with AI… this may take 10–20 seconds',
                style: TextStyle(
                    color: AppColors.textSecondary, fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ] else
              FilledButton.icon(
                onPressed: _pickedFile?.path != null ? _upload : null,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Extract with AI'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.all(16),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardDark,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'We extract from your 1040:',
            style: const TextStyle(
                fontWeight: FontWeight.w600, fontSize: 13),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: [
              'AGI',
              'Total Income',
              'Taxable Income',
              'Total Tax',
              'Filing Status',
              'Federal Withheld',
              'Refund / Owed',
              'Deductions',
            ]
                .map((label) => Chip(
                      label: Text(label, style: const TextStyle(fontSize: 11)),
                      padding: EdgeInsets.zero,
                      visualDensity: VisualDensity.compact,
                      backgroundColor: AppColors.brand.withAlpha(30),
                    ))
                .toList(),
          ),
        ],
      ),
    );
  }
}
