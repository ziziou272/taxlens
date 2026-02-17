// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tax_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$TaxResultImpl _$$TaxResultImplFromJson(Map<String, dynamic> json) =>
    _$TaxResultImpl(
      totalIncome: (json['totalIncome'] as num).toDouble(),
      federalTax: (json['federalTax'] as num).toDouble(),
      stateTax: (json['stateTax'] as num).toDouble(),
      totalTax: (json['totalTax'] as num).toDouble(),
      effectiveRate: (json['effectiveRate'] as num).toDouble(),
      marginalRate: (json['marginalRate'] as num).toDouble(),
      totalWithheld: (json['totalWithheld'] as num).toDouble(),
      amountOwed: (json['amountOwed'] as num).toDouble(),
      incomeBreakdown: (json['incomeBreakdown'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      taxableIncome: (json['taxableIncome'] as num?)?.toDouble() ?? 0,
      deductionUsed: (json['deductionUsed'] as num?)?.toDouble() ?? 0,
      socialSecurityTax: (json['socialSecurityTax'] as num?)?.toDouble() ?? 0,
      medicareTax: (json['medicareTax'] as num?)?.toDouble() ?? 0,
      childTaxCredit: (json['childTaxCredit'] as num?)?.toDouble() ?? 0,
      otherDependentCredit:
          (json['otherDependentCredit'] as num?)?.toDouble() ?? 0,
      actc: (json['actc'] as num?)?.toDouble() ?? 0,
      eitc: (json['eitc'] as num?)?.toDouble() ?? 0,
      educationCredit: (json['educationCredit'] as num?)?.toDouble() ?? 0,
      educationCreditRefundable:
          (json['educationCreditRefundable'] as num?)?.toDouble() ?? 0,
      totalCredits: (json['totalCredits'] as num?)?.toDouble() ?? 0,
      agi: (json['agi'] as num?)?.toDouble() ?? 0,
      itemizedDeductionsTotal:
          (json['itemizedDeductionsTotal'] as num?)?.toDouble() ?? 0,
      aboveTheLineDeductionsTotal:
          (json['aboveTheLineDeductionsTotal'] as num?)?.toDouble() ?? 0,
    );

Map<String, dynamic> _$$TaxResultImplToJson(_$TaxResultImpl instance) =>
    <String, dynamic>{
      'totalIncome': instance.totalIncome,
      'federalTax': instance.federalTax,
      'stateTax': instance.stateTax,
      'totalTax': instance.totalTax,
      'effectiveRate': instance.effectiveRate,
      'marginalRate': instance.marginalRate,
      'totalWithheld': instance.totalWithheld,
      'amountOwed': instance.amountOwed,
      'incomeBreakdown': instance.incomeBreakdown,
      'taxableIncome': instance.taxableIncome,
      'deductionUsed': instance.deductionUsed,
      'socialSecurityTax': instance.socialSecurityTax,
      'medicareTax': instance.medicareTax,
      'childTaxCredit': instance.childTaxCredit,
      'otherDependentCredit': instance.otherDependentCredit,
      'actc': instance.actc,
      'eitc': instance.eitc,
      'educationCredit': instance.educationCredit,
      'educationCreditRefundable': instance.educationCreditRefundable,
      'totalCredits': instance.totalCredits,
      'agi': instance.agi,
      'itemizedDeductionsTotal': instance.itemizedDeductionsTotal,
      'aboveTheLineDeductionsTotal': instance.aboveTheLineDeductionsTotal,
    };
