import 'package:intl/intl.dart';

final _currencyFmt = NumberFormat.currency(symbol: r'$', decimalDigits: 0);

class TaxReturn {
  const TaxReturn({
    required this.id,
    required this.taxYear,
    required this.source,
    this.filingStatus,
    this.totalIncome,
    this.adjustedGrossIncome,
    this.deductionType,
    this.deductionAmount,
    this.taxableIncome,
    this.totalTax,
    this.totalCredits,
    this.federalWithheld,
    this.refundOrOwed,
    this.scheduleData,
    this.extractionConfidence,
    this.userConfirmed = false,
    required this.createdAt,
  });

  final String id;
  final int taxYear;
  final String source; // 'pdf_upload', 'manual', 'irs_transcript'
  final String? filingStatus;
  final double? totalIncome;
  final double? adjustedGrossIncome;
  final String? deductionType;
  final double? deductionAmount;
  final double? taxableIncome;
  final double? totalTax;
  final double? totalCredits;
  final double? federalWithheld;
  final double? refundOrOwed;
  final Map<String, dynamic>? scheduleData;
  final double? extractionConfidence;
  final bool userConfirmed;
  final DateTime createdAt;

  factory TaxReturn.fromJson(Map<String, dynamic> json) {
    return TaxReturn(
      id: json['id'] as String? ?? '',
      taxYear: (json['tax_year'] as num?)?.toInt() ?? 0,
      source: json['source'] as String? ?? 'pdf_upload',
      filingStatus: json['filing_status'] as String?,
      totalIncome: (json['total_income'] as num?)?.toDouble(),
      adjustedGrossIncome: (json['adjusted_gross_income'] as num?)?.toDouble(),
      deductionType: json['deduction_type'] as String?,
      deductionAmount: (json['deduction_amount'] as num?)?.toDouble(),
      taxableIncome: (json['taxable_income'] as num?)?.toDouble(),
      totalTax: (json['total_tax'] as num?)?.toDouble(),
      totalCredits: (json['total_credits'] as num?)?.toDouble(),
      federalWithheld: (json['federal_withheld'] as num?)?.toDouble(),
      refundOrOwed: (json['refund_or_owed'] as num?)?.toDouble(),
      scheduleData: json['schedule_data'] as Map<String, dynamic>?,
      extractionConfidence:
          (json['extraction_confidence'] as num?)?.toDouble(),
      userConfirmed: json['user_confirmed'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
        'tax_year': taxYear,
        'source': source,
        if (filingStatus != null) 'filing_status': filingStatus,
        if (totalIncome != null) 'total_income': totalIncome,
        if (adjustedGrossIncome != null)
          'adjusted_gross_income': adjustedGrossIncome,
        if (deductionType != null) 'deduction_type': deductionType,
        if (deductionAmount != null) 'deduction_amount': deductionAmount,
        if (taxableIncome != null) 'taxable_income': taxableIncome,
        if (totalTax != null) 'total_tax': totalTax,
        if (totalCredits != null) 'total_credits': totalCredits,
        if (federalWithheld != null) 'federal_withheld': federalWithheld,
        if (refundOrOwed != null) 'refund_or_owed': refundOrOwed,
        if (scheduleData != null) 'schedule_data': scheduleData,
      };

  String get filingStatusLabel {
    switch (filingStatus) {
      case 'single':
        return 'Single';
      case 'married_filing_jointly':
        return 'Married Filing Jointly';
      case 'married_filing_separately':
        return 'Married Filing Separately';
      case 'head_of_household':
        return 'Head of Household';
      default:
        return filingStatus ?? 'Unknown';
    }
  }

  String get effectiveTaxRateLabel {
    if (totalTax == null || totalIncome == null || totalIncome == 0) {
      return '—';
    }
    final rate = (totalTax! / totalIncome!) * 100;
    return '${rate.toStringAsFixed(1)}%';
  }

  String get refundOrOwedLabel {
    if (refundOrOwed == null) return '—';
    if (refundOrOwed! >= 0) {
      return 'Refund: ${_currencyFmt.format(refundOrOwed!)}';
    } else {
      return 'Owed: ${_currencyFmt.format(refundOrOwed!.abs())}';
    }
  }
}

/// Data extracted from PDF upload, before user confirmation.
class TaxReturnExtraction {
  const TaxReturnExtraction({
    required this.taxYear,
    this.filingStatus,
    this.totalIncome,
    this.adjustedGrossIncome,
    this.deductionType,
    this.deductionAmount,
    this.taxableIncome,
    this.totalTax,
    this.totalCredits,
    this.federalWithheld,
    this.refundOrOwed,
    this.extractionConfidence,
    this.fieldConfidence,
  });

  final int taxYear;
  final String? filingStatus;
  final double? totalIncome;
  final double? adjustedGrossIncome;
  final String? deductionType;
  final double? deductionAmount;
  final double? taxableIncome;
  final double? totalTax;
  final double? totalCredits;
  final double? federalWithheld;
  final double? refundOrOwed;
  final double? extractionConfidence;
  final Map<String, double>? fieldConfidence;

  factory TaxReturnExtraction.fromJson(Map<String, dynamic> json) {
    Map<String, double>? fieldConf;
    if (json['field_confidence'] != null) {
      final raw = json['field_confidence'] as Map<String, dynamic>;
      fieldConf = raw.map((k, v) => MapEntry(k, (v as num).toDouble()));
    }
    return TaxReturnExtraction(
      taxYear: (json['tax_year'] as num?)?.toInt() ?? DateTime.now().year - 1,
      filingStatus: json['filing_status'] as String?,
      totalIncome: (json['total_income'] as num?)?.toDouble(),
      adjustedGrossIncome: (json['adjusted_gross_income'] as num?)?.toDouble(),
      deductionType: json['deduction_type'] as String?,
      deductionAmount: (json['deduction_amount'] as num?)?.toDouble(),
      taxableIncome: (json['taxable_income'] as num?)?.toDouble(),
      totalTax: (json['total_tax'] as num?)?.toDouble(),
      totalCredits: (json['total_credits'] as num?)?.toDouble(),
      federalWithheld: (json['federal_withheld'] as num?)?.toDouble(),
      refundOrOwed: (json['refund_or_owed'] as num?)?.toDouble(),
      extractionConfidence:
          (json['extraction_confidence'] as num?)?.toDouble(),
      fieldConfidence: fieldConf,
    );
  }

  double confidenceFor(String field) {
    return fieldConfidence?[field] ?? extractionConfidence ?? 0.8;
  }

  Map<String, String> toEditableFields() => {
        'tax_year': taxYear.toString(),
        'filing_status': filingStatus ?? '',
        'total_income': totalIncome?.toStringAsFixed(2) ?? '',
        'adjusted_gross_income': adjustedGrossIncome?.toStringAsFixed(2) ?? '',
        'deduction_type': deductionType ?? '',
        'deduction_amount': deductionAmount?.toStringAsFixed(2) ?? '',
        'taxable_income': taxableIncome?.toStringAsFixed(2) ?? '',
        'total_tax': totalTax?.toStringAsFixed(2) ?? '',
        'total_credits': totalCredits?.toStringAsFixed(2) ?? '',
        'federal_withheld': federalWithheld?.toStringAsFixed(2) ?? '',
        'refund_or_owed': refundOrOwed?.toStringAsFixed(2) ?? '',
      };

  Map<String, dynamic> toConfirmJson(Map<String, String> editedFields) {
    double? parseField(String key) {
      final v = editedFields[key];
      if (v == null || v.isEmpty) return null;
      return double.tryParse(v.replaceAll(',', ''));
    }

    return {
      'tax_year': int.tryParse(editedFields['tax_year'] ?? '') ?? taxYear,
      'source': 'pdf_upload',
      'filing_status': editedFields['filing_status'],
      'total_income': parseField('total_income'),
      'adjusted_gross_income': parseField('adjusted_gross_income'),
      'deduction_type': editedFields['deduction_type'],
      'deduction_amount': parseField('deduction_amount'),
      'taxable_income': parseField('taxable_income'),
      'total_tax': parseField('total_tax'),
      'total_credits': parseField('total_credits'),
      'federal_withheld': parseField('federal_withheld'),
      'refund_or_owed': parseField('refund_or_owed'),
    };
  }
}
