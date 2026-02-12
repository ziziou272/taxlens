import 'package:flutter_riverpod/flutter_riverpod.dart';

enum DocumentType { w2, form1099B, form1099DIV, form3922 }

enum DocumentStatus { processing, reviewNeeded, confirmed }

class TaxDocument {
  const TaxDocument({
    required this.id,
    required this.type,
    required this.fileName,
    required this.status,
    required this.uploadDate,
    this.extractedData,
  });

  final String id;
  final DocumentType type;
  final String fileName;
  final DocumentStatus status;
  final DateTime uploadDate;
  final Map<String, String>? extractedData;

  String get typeLabel {
    switch (type) {
      case DocumentType.w2:
        return 'W-2';
      case DocumentType.form1099B:
        return '1099-B';
      case DocumentType.form1099DIV:
        return '1099-DIV';
      case DocumentType.form3922:
        return 'Form 3922';
    }
  }

  String get statusLabel {
    switch (status) {
      case DocumentStatus.processing:
        return 'Processing';
      case DocumentStatus.reviewNeeded:
        return 'Review Needed';
      case DocumentStatus.confirmed:
        return 'Confirmed';
    }
  }

  TaxDocument copyWith({
    DocumentStatus? status,
    Map<String, String>? extractedData,
  }) {
    return TaxDocument(
      id: id,
      type: type,
      fileName: fileName,
      status: status ?? this.status,
      uploadDate: uploadDate,
      extractedData: extractedData ?? this.extractedData,
    );
  }
}

Map<String, String> _w2Fields() => {
      'Employer Name': 'Acme Corp',
      'Wages': '185,000.00',
      'Federal Withholding': '38,200.00',
      'State Withholding': '12,450.00',
      'Box 12 Codes': 'D: 22,500 / DD: 8,400',
    };

Map<String, String> _form1099BFields() => {
      'Proceeds': '45,200.00',
      'Cost Basis': '32,100.00',
      'Gain/Loss': '13,100.00',
      'Date Acquired': '03/15/2023',
      'Date Sold': '11/20/2025',
      'Term': 'Long-term',
    };

Map<String, String> _form1099DivFields() => {
      'Ordinary Dividends': '3,200.00',
      'Qualified Dividends': '2,800.00',
      'Total Capital Gain': '1,450.00',
    };

final documentsProvider =
    StateNotifierProvider<DocumentsNotifier, List<TaxDocument>>((ref) {
  return DocumentsNotifier();
});

class DocumentsNotifier extends StateNotifier<List<TaxDocument>> {
  DocumentsNotifier()
      : super([
          TaxDocument(
            id: '1',
            type: DocumentType.w2,
            fileName: 'w2_acme_2025.pdf',
            status: DocumentStatus.confirmed,
            uploadDate: DateTime(2025, 12, 15),
            extractedData: _w2Fields(),
          ),
          TaxDocument(
            id: '2',
            type: DocumentType.form1099B,
            fileName: '1099b_schwab.pdf',
            status: DocumentStatus.reviewNeeded,
            uploadDate: DateTime(2026, 1, 20),
            extractedData: _form1099BFields(),
          ),
          TaxDocument(
            id: '3',
            type: DocumentType.form1099DIV,
            fileName: '1099div_vanguard.pdf',
            status: DocumentStatus.reviewNeeded,
            uploadDate: DateTime(2026, 2, 1),
            extractedData: _form1099DivFields(),
          ),
        ]);

  void addDocument(TaxDocument doc) {
    state = [...state, doc];
  }

  void confirmDocument(String id) {
    state = [
      for (final doc in state)
        if (doc.id == id)
          doc.copyWith(status: DocumentStatus.confirmed)
        else
          doc,
    ];
  }

  void updateExtractedData(String id, Map<String, String> data) {
    state = [
      for (final doc in state)
        if (doc.id == id)
          doc.copyWith(
            extractedData: data,
            status: DocumentStatus.reviewNeeded,
          )
        else
          doc,
    ];
  }
}

final documentDetailProvider =
    Provider.family<TaxDocument?, String>((ref, id) {
  final docs = ref.watch(documentsProvider);
  try {
    return docs.firstWhere((d) => d.id == id);
  } catch (_) {
    return null;
  }
});
