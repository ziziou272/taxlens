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
    // Credits
    @Default(0) double childTaxCredit,
    @Default(0) double otherDependentCredit,
    @Default(0) double actc,
    @Default(0) double eitc,
    @Default(0) double educationCredit,
    @Default(0) double educationCreditRefundable,
    @Default(0) double totalCredits,
    // AGI & deduction detail
    @Default(0) double agi,
    @Default(0) double itemizedDeductionsTotal,
    @Default(0) double aboveTheLineDeductionsTotal,
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

    // above_the_line_deductions is an object with a .total field
    final aboveTheLineObj = json['above_the_line_deductions'];
    final aboveTheLineTotal = aboveTheLineObj is Map
        ? (aboveTheLineObj['total'] as num?)?.toDouble() ?? 0
        : (aboveTheLineObj as num?)?.toDouble() ?? 0;

    // itemized_deductions_detail is an object with a .total field
    final itemizedObj = json['itemized_deductions_detail'];
    final itemizedTotal = itemizedObj is Map
        ? (itemizedObj['total'] as num?)?.toDouble() ?? 0
        : (itemizedObj as num?)?.toDouble() ?? 0;

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
      socialSecurityTax:
          (json['social_security_tax'] as num?)?.toDouble() ?? 0,
      medicareTax: (json['medicare_tax'] as num?)?.toDouble() ?? 0,
      incomeBreakdown: {'Total Income': totalIncome},
      // Credits
      childTaxCredit:
          (json['child_tax_credit'] as num?)?.toDouble() ?? 0,
      otherDependentCredit:
          (json['other_dependent_credit'] as num?)?.toDouble() ?? 0,
      actc: (json['actc'] as num?)?.toDouble() ?? 0,
      eitc: (json['eitc'] as num?)?.toDouble() ?? 0,
      educationCredit:
          (json['education_credit'] as num?)?.toDouble() ?? 0,
      educationCreditRefundable:
          (json['education_credit_refundable'] as num?)?.toDouble() ?? 0,
      totalCredits: (json['total_credits'] as num?)?.toDouble() ?? 0,
      // AGI & deduction detail
      agi: (json['agi'] as num?)?.toDouble() ?? 0,
      itemizedDeductionsTotal: itemizedTotal,
      aboveTheLineDeductionsTotal: aboveTheLineTotal,
    );
  }
}
