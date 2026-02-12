import 'package:freezed_annotation/freezed_annotation.dart';

part 'tax_result.freezed.dart';
part 'tax_result.g.dart';

@freezed
class TaxResult with _$TaxResult {
  const factory TaxResult({
    required double totalIncome,
    required double federalTax,
    required double stateTax,
    required double totalTax,
    required double effectiveRate,
    required double marginalRate,
    required double totalWithheld,
    required double amountOwed,
    required Map<String, double> incomeBreakdown,
  }) = _TaxResult;

  factory TaxResult.fromJson(Map<String, dynamic> json) =>
      _$TaxResultFromJson(json);
}
