import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';
import '../../core/theme/app_colors.dart';
import 'documents_provider.dart';

class DocumentUploadScreen extends ConsumerStatefulWidget {
  const DocumentUploadScreen({super.key});

  @override
  ConsumerState<DocumentUploadScreen> createState() =>
      _DocumentUploadScreenState();
}

class _DocumentUploadScreenState extends ConsumerState<DocumentUploadScreen> {
  DocumentType _selectedType = DocumentType.w2;
  String? _fileName;
  bool _uploading = false;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() => _fileName = result.files.first.name);
    }
  }

  Future<void> _upload() async {
    if (_fileName == null) return;
    setState(() => _uploading = true);

    // Simulate upload delay
    await Future<void>.delayed(const Duration(seconds: 2));

    if (!mounted) return;

    final id = DateTime.now().millisecondsSinceEpoch.toString();
    ref.read(documentsProvider.notifier).addDocument(
          TaxDocument(
            id: id,
            type: _selectedType,
            fileName: _fileName!,
            status: DocumentStatus.processing,
            uploadDate: DateTime.now(),
          ),
        );

    setState(() => _uploading = false);
    if (mounted) context.go('/documents/$id');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Document')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Document Type',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            SegmentedButton<DocumentType>(
              segments: const [
                ButtonSegment(value: DocumentType.w2, label: Text('W-2')),
                ButtonSegment(
                    value: DocumentType.form1099B, label: Text('1099-B')),
                ButtonSegment(
                    value: DocumentType.form1099DIV, label: Text('1099-DIV')),
                ButtonSegment(
                    value: DocumentType.form3922, label: Text('3922')),
              ],
              selected: {_selectedType},
              onSelectionChanged: (v) =>
                  setState(() => _selectedType = v.first),
            ),
            const SizedBox(height: 32),
            OutlinedButton.icon(
              onPressed: _uploading ? null : _pickFile,
              icon: const Icon(Icons.attach_file),
              label: Text(_fileName ?? 'Select File (PDF, JPG, PNG)'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.all(20),
              ),
            ),
            if (_fileName != null) ...[
              const SizedBox(height: 8),
              Text(_fileName!,
                  style: TextStyle(color: AppColors.textSecondary),
                  textAlign: TextAlign.center),
            ],
            const Spacer(),
            if (_uploading)
              const Center(child: CircularProgressIndicator())
            else
              FilledButton.icon(
                onPressed: _fileName != null ? _upload : null,
                icon: const Icon(Icons.cloud_upload),
                label: const Text('Upload & Extract'),
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
