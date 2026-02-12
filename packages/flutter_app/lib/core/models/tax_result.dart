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
    @Default(0) double taxableIncome,
    @Default(0) double deductionUsed,
    @Default(0) double socialSecurityTax,
    @Default(0) double medicareTax,
  }) = _TaxResult;

  factory TaxResult.fromJson(Map<String, dynamic> json) =>
      _$TaxResultFromJson(json);

  /// Create from the backend TaxBreakdownResponse shape.
  factory TaxResult.fromApiResponse(Map<String, dynamic> json) {
    final federalTax = (json['federal_tax'] as num?)?.toDouble() ?? 0;
    final stateTax = (json['state_tax'] as num?)?.toDouble() ?? 0;
    final totalTax = (json['total_tax'] as num?)?.toDouble() ?? 0;
    final totalIncome = (json['total_income'] as num?)?.toDouble() ?? 0;
    final balanceDue = (json['balance_due'] as num?)?.toDouble() ?? 0;

    return TaxResult(
      totalIncome: totalIncome,
      federalTax: federalTax,
      stateTax: stateTax,
      totalTax: totalTax,
      effectiveRate: (json['effective_rate'] as num?)?.toDouble() ?? 0,
      marginalRate: (json['marginal_rate'] as num?)?.toDouble() ?? 0,
      totalWithheld: totalTax - balanceDue,
      amountOwed: balanceDue,
      taxableIncome: (json['taxable_income'] as num?)?.toDouble() ?? 0,
      deductionUsed: (json['deduction_used'] as num?)?.toDouble() ?? 0,
      socialSecurityTax: (json['social_security_tax'] as num?)?.toDouble() ?? 0,
      medicareTax: (json['medicare_tax'] as num?)?.toDouble() ?? 0,
      incomeBreakdown: {'Total Income': totalIncome},
    );
  }
}
