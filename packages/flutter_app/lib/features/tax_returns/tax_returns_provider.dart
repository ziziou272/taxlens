import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/api_provider.dart';
import 'tax_return_model.dart';

// ── State ─────────────────────────────────────────────────────────────────

/// All imported tax returns from the backend.
final taxReturnsProvider =
    AsyncNotifierProvider<TaxReturnsNotifier, List<TaxReturn>>(
  TaxReturnsNotifier.new,
);

class TaxReturnsNotifier extends AsyncNotifier<List<TaxReturn>> {
  @override
  Future<List<TaxReturn>> build() async {
    return _fetchAll();
  }

  Future<List<TaxReturn>> _fetchAll() async {
    final api = ref.read(apiClientProvider);
    return api.getTaxReturns();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetchAll);
  }

  Future<TaxReturn> confirmExtraction(Map<String, dynamic> data) async {
    final api = ref.read(apiClientProvider);
    final saved = await api.confirmTaxReturn(data);
    // Optimistically add to list
    state.whenData((list) {
      final updated = [...list.where((r) => r.taxYear != saved.taxYear), saved]
        ..sort((a, b) => b.taxYear.compareTo(a.taxYear));
      state = AsyncData(updated);
    });
    return saved;
  }

  Future<void> deleteYear(int year) async {
    final api = ref.read(apiClientProvider);
    await api.deleteTaxReturn(year);
    state.whenData((list) {
      state = AsyncData(list.where((r) => r.taxYear != year).toList());
    });
  }
}

/// Single tax return detail provider (by year).
final taxReturnDetailProvider =
    AsyncNotifierProviderFamily<TaxReturnDetailNotifier, TaxReturn?, int>(
  TaxReturnDetailNotifier.new,
);

class TaxReturnDetailNotifier extends FamilyAsyncNotifier<TaxReturn?, int> {
  @override
  Future<TaxReturn?> build(int arg) async {
    // First check local cache
    final cached = ref.read(taxReturnsProvider).valueOrNull;
    if (cached != null) {
      try {
        return cached.firstWhere((r) => r.taxYear == arg);
      } catch (_) {}
    }
    // Fetch from API
    final api = ref.read(apiClientProvider);
    return api.getTaxReturn(arg);
  }
}

/// Upload state machine.
enum UploadStatus { idle, picking, uploading, done, error }

class UploadState {
  const UploadState({
    this.status = UploadStatus.idle,
    this.fileName,
    this.extraction,
    this.error,
  });

  final UploadStatus status;
  final String? fileName;
  final TaxReturnExtraction? extraction;
  final String? error;

  UploadState copyWith({
    UploadStatus? status,
    String? fileName,
    TaxReturnExtraction? extraction,
    String? error,
  }) {
    return UploadState(
      status: status ?? this.status,
      fileName: fileName ?? this.fileName,
      extraction: extraction ?? this.extraction,
      error: error,
    );
  }
}

final uploadPdfProvider =
    StateNotifierProvider.autoDispose<UploadPdfNotifier, UploadState>(
  (ref) => UploadPdfNotifier(ref),
);

class UploadPdfNotifier extends StateNotifier<UploadState> {
  UploadPdfNotifier(this._ref) : super(const UploadState());

  final Ref _ref;

  Future<TaxReturnExtraction?> upload(String filePath, String fileName) async {
    state = UploadState(
      status: UploadStatus.uploading,
      fileName: fileName,
    );
    try {
      final api = _ref.read(apiClientProvider);
      final extraction = await api.uploadTaxReturnPdf(filePath, fileName: fileName);
      state = UploadState(
        status: UploadStatus.done,
        fileName: fileName,
        extraction: extraction,
      );
      return extraction;
    } catch (e) {
      state = UploadState(
        status: UploadStatus.error,
        fileName: fileName,
        error: e.toString(),
      );
      return null;
    }
  }

  void reset() {
    state = const UploadState();
  }
}
