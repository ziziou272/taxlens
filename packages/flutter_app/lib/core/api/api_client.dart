import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart' hide MultipartFile;

import '../models/tax_result.dart';
import '../../features/tax_returns/tax_return_model.dart';
import 'api_endpoints.dart';

class ApiException implements Exception {
  final String message;
  const ApiException(this.message);

  @override
  String toString() => message;
}

/// Callback invoked when a 401 response is received.
typedef OnUnauthorized = void Function();

class ApiClient {
  ApiClient({
    String baseUrl = 'https://taxlens.ziziou.com',
    this.supabaseAvailable = false,
    this.onUnauthorized,
  }) : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          headers: {'Content-Type': 'application/json'},
        )) {
    _dio.interceptors.add(LogInterceptor(responseBody: true));

    // Auth interceptor: attach JWT & handle 401s
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (supabaseAvailable) {
          final session = Supabase.instance.client.auth.currentSession;
          if (session != null) {
            options.headers['Authorization'] = 'Bearer ${session.accessToken}';
          }
        }
        handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          onUnauthorized?.call();
        }
        handler.next(error);
      },
    ));
  }

  final Dio _dio;
  final bool supabaseAvailable;
  OnUnauthorized? onUnauthorized;

  Dio get dio => _dio;

  void updateBaseUrl(String baseUrl) {
    _dio.options.baseUrl = baseUrl;
  }

  Future<TaxResult> calculateTax(TaxInput input) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.calculate,
        data: input.toJson(),
      );
      return TaxResult.fromApiResponse(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  Future<AlertCheckResult> checkAlerts(AlertCheckInput input) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.alertsCheck,
        data: input.toJson(),
      );
      return AlertCheckResult.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  Future<List<ScenarioType>> getScenarioTypes() async {
    try {
      final response = await _dio.get(ApiEndpoints.scenarioTypes);
      final list = response.data as List;
      return list
          .map((e) => ScenarioType.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  Future<ScenarioComparison> runScenario(ScenarioRunInput input) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.scenarioRun,
        data: input.toJson(),
      );
      return ScenarioComparison.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  Future<WithholdingGap> getWithholdingGap(WithholdingGapInput input) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.withholdingGap,
        data: input.toJson(),
      );
      return WithholdingGap.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  Future<Map<String, dynamic>> dismissAlert(String alertId) async {
    try {
      final response = await _dio.post('/api/alerts/$alertId/dismiss');
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  String _friendlyError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Request timed out. Please try again.';
      case DioExceptionType.connectionError:
        return 'Cannot connect to server. Check your connection.';
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        final detail = e.response?.data is Map
            ? (e.response!.data as Map)['detail'] ?? ''
            : '';
        if (statusCode == 422) return 'Invalid input: $detail';
        if (statusCode >= 500) return 'Server error. Please try again later.';
        return 'Request failed ($statusCode): $detail';
      default:
        return 'Something went wrong. Please try again.';
    }
  }

  Future<Response<T>> get<T>(String path,
      {Map<String, dynamic>? queryParameters}) {
    return _dio.get<T>(path, queryParameters: queryParameters);
  }

  Future<Response<T>> post<T>(String path, {Object? data}) {
    return _dio.post<T>(path, data: data);
  }

  // ── Tax Returns ──────────────────────────────────────────────────────────

  /// Upload a 1040 PDF for AI extraction. Returns extracted fields + confidence.
  Future<TaxReturnExtraction> uploadTaxReturnPdf(String filePath,
      {String? fileName}) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          filename: fileName ?? filePath.split('/').last,
        ),
      });
      final response = await _dio.post(
        ApiEndpoints.taxReturnUploadPdf,
        data: formData,
        options: Options(
          headers: {'Content-Type': 'multipart/form-data'},
          receiveTimeout: const Duration(seconds: 60), // PDF extraction takes time
        ),
      );
      return TaxReturnExtraction.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  /// Confirm extracted (or manually entered) tax return data, saving to DB.
  Future<TaxReturn> confirmTaxReturn(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.taxReturnConfirm,
        data: data,
      );
      return TaxReturn.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  /// List all imported tax years.
  Future<List<TaxReturn>> getTaxReturns() async {
    try {
      final response = await _dio.get(ApiEndpoints.taxReturns);
      final list = response.data as List;
      return list
          .map((e) => TaxReturn.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  /// Get data for a specific tax year.
  Future<TaxReturn> getTaxReturn(int year) async {
    try {
      final response = await _dio.get(ApiEndpoints.taxReturnYear(year));
      return TaxReturn.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }

  /// Delete a specific tax year's data.
  Future<void> deleteTaxReturn(int year) async {
    try {
      await _dio.delete(ApiEndpoints.taxReturnYear(year));
    } on DioException catch (e) {
      throw ApiException(_friendlyError(e));
    }
  }
}

/// Input model for tax calculation — maps to backend TaxInput schema.
class TaxInput {
  final String filingStatus;
  final double wages;
  final double rsuIncome;
  final double capitalGainsShort;
  final double capitalGainsLong;
  final String state;
  final double federalWithheld;
  final double stateWithheld;

  // Deductions
  final double mortgageInterest;
  final double saltPaid;
  final double charitableContributions;
  final double medicalExpenses;

  // Retirement & Pre-tax
  final double contributions401k;
  final double iraContributions;
  final double hsaContributions;
  final double studentLoanInterest;

  // Family & Education
  final int numChildrenUnder17;
  final int numOtherDependents;
  final double educationExpenses;
  final String educationType;
  final bool ageOver50;

  const TaxInput({
    this.filingStatus = 'single',
    this.wages = 0,
    this.rsuIncome = 0,
    this.capitalGainsShort = 0,
    this.capitalGainsLong = 0,
    this.state = 'CA',
    this.federalWithheld = 0,
    this.stateWithheld = 0,
    // Deductions
    this.mortgageInterest = 0,
    this.saltPaid = 0,
    this.charitableContributions = 0,
    this.medicalExpenses = 0,
    // Retirement & Pre-tax
    this.contributions401k = 0,
    this.iraContributions = 0,
    this.hsaContributions = 0,
    this.studentLoanInterest = 0,
    // Family & Education
    this.numChildrenUnder17 = 0,
    this.numOtherDependents = 0,
    this.educationExpenses = 0,
    this.educationType = 'none',
    this.ageOver50 = false,
  });

  Map<String, dynamic> toJson() => {
        'filing_status': filingStatus,
        'wages': wages,
        'rsu_income': rsuIncome,
        'capital_gains_short': capitalGainsShort,
        'capital_gains_long': capitalGainsLong,
        'state': state,
        'federal_withheld': federalWithheld,
        'state_withheld': stateWithheld,
        // Deductions
        'mortgage_interest': mortgageInterest,
        'salt_paid': saltPaid,
        'charitable_contributions': charitableContributions,
        'medical_expenses': medicalExpenses,
        // Retirement & Pre-tax
        'contributions_401k': contributions401k,
        'ira_contributions': iraContributions,
        'hsa_contributions': hsaContributions,
        'student_loan_interest': studentLoanInterest,
        // Family & Education
        'num_children_under_17': numChildrenUnder17,
        'num_other_dependents': numOtherDependents,
        'education_expenses': educationExpenses,
        'education_type': educationType,
        'age_over_50': ageOver50,
      };
}

/// Input for alert checking.
class AlertCheckInput {
  final double totalIncome;
  final double totalTaxLiability;
  final double totalWithheld;
  final double longTermGains;
  final double shortTermGains;
  final double rsuIncome;
  final String filingStatus;
  final String state;

  const AlertCheckInput({
    this.totalIncome = 0,
    this.totalTaxLiability = 0,
    this.totalWithheld = 0,
    this.longTermGains = 0,
    this.shortTermGains = 0,
    this.rsuIncome = 0,
    this.filingStatus = 'single',
    this.state = 'CA',
  });

  Map<String, dynamic> toJson() => {
        'total_income': totalIncome,
        'total_tax_liability': totalTaxLiability,
        'total_withheld': totalWithheld,
        'long_term_gains': longTermGains,
        'short_term_gains': shortTermGains,
        'rsu_income': rsuIncome,
        'filing_status': filingStatus,
        'state': state,
      };
}

/// Parsed alert result from API.
class AlertCheckResult {
  final String summary;
  final List<ApiAlert> alerts;
  final bool hasCritical;

  const AlertCheckResult({
    required this.summary,
    required this.alerts,
    required this.hasCritical,
  });

  factory AlertCheckResult.fromJson(Map<String, dynamic> json) {
    return AlertCheckResult(
      summary: json['summary'] as String? ?? '',
      alerts: (json['alerts'] as List?)
              ?.map((e) => ApiAlert.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      hasCritical: json['has_critical'] as bool? ?? false,
    );
  }
}

class ApiAlert {
  final String severity;
  final String category;
  final String title;
  final String message;
  final double? amount;
  final String? actionRequired;

  const ApiAlert({
    required this.severity,
    required this.category,
    required this.title,
    required this.message,
    this.amount,
    this.actionRequired,
  });

  factory ApiAlert.fromJson(Map<String, dynamic> json) {
    return ApiAlert(
      severity: json['severity'] as String? ?? 'info',
      category: json['category'] as String? ?? '',
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      amount: (json['amount'] as num?)?.toDouble(),
      actionRequired: json['action_required'] as String?,
    );
  }
}

/// Withholding gap input.
class WithholdingGapInput {
  final String filingStatus;
  final double wages;
  final double rsuIncome;
  final double capitalGainsLong;
  final String state;
  final double ytdFederalWithheld;
  final double ytdStateWithheld;

  const WithholdingGapInput({
    this.filingStatus = 'single',
    this.wages = 0,
    this.rsuIncome = 0,
    this.capitalGainsLong = 0,
    this.state = 'CA',
    this.ytdFederalWithheld = 0,
    this.ytdStateWithheld = 0,
  });

  Map<String, dynamic> toJson() => {
        'filing_status': filingStatus,
        'wages': wages,
        'rsu_income': rsuIncome,
        'capital_gains_long': capitalGainsLong,
        'state': state,
        'ytd_federal_withheld': ytdFederalWithheld,
        'ytd_state_withheld': ytdStateWithheld,
      };
}

/// Withholding gap response.
class WithholdingGap {
  final double projectedTotalTax;
  final double ytdWithheld;
  final double gap;
  final double gapPercentage;
  final double quarterlyPaymentNeeded;

  const WithholdingGap({
    required this.projectedTotalTax,
    required this.ytdWithheld,
    required this.gap,
    required this.gapPercentage,
    required this.quarterlyPaymentNeeded,
  });

  factory WithholdingGap.fromJson(Map<String, dynamic> json) {
    return WithholdingGap(
      projectedTotalTax: (json['projected_total_tax'] as num?)?.toDouble() ?? 0,
      ytdWithheld: (json['ytd_withheld'] as num?)?.toDouble() ?? 0,
      gap: (json['gap'] as num?)?.toDouble() ?? 0,
      gapPercentage: (json['gap_percentage'] as num?)?.toDouble() ?? 0,
      quarterlyPaymentNeeded:
          (json['quarterly_payment_needed'] as num?)?.toDouble() ?? 0,
    );
  }
}

/// Scenario types from backend.
class ScenarioType {
  final String typeId;
  final String name;
  final String description;

  const ScenarioType({
    required this.typeId,
    required this.name,
    required this.description,
  });

  factory ScenarioType.fromJson(Map<String, dynamic> json) {
    return ScenarioType(
      typeId: json['type_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String? ?? '',
    );
  }
}

/// Scenario run input.
class ScenarioRunInput {
  final Map<String, dynamic> baseline;
  final Map<String, dynamic> alternative;

  const ScenarioRunInput({required this.baseline, required this.alternative});

  Map<String, dynamic> toJson() => {
        'baseline': baseline,
        'alternative': alternative,
      };
}

/// Scenario comparison from backend.
class ScenarioComparison {
  final ScenarioResultData baseline;
  final ScenarioResultData alternative;
  final double taxSavings;
  final double savingsPercentage;
  final Map<String, double> breakdownDiff;

  const ScenarioComparison({
    required this.baseline,
    required this.alternative,
    required this.taxSavings,
    required this.savingsPercentage,
    this.breakdownDiff = const {},
  });

  factory ScenarioComparison.fromJson(Map<String, dynamic> json) {
    final diffRaw = json['breakdown_diff'] as Map<String, dynamic>? ?? {};
    final diff = diffRaw.map((k, v) => MapEntry(k, (v as num?)?.toDouble() ?? 0));
    return ScenarioComparison(
      baseline: ScenarioResultData.fromJson(
          json['baseline'] as Map<String, dynamic>),
      alternative: ScenarioResultData.fromJson(
          json['alternative'] as Map<String, dynamic>),
      taxSavings: (json['tax_savings'] as num?)?.toDouble() ?? 0,
      savingsPercentage:
          (json['savings_percentage'] as num?)?.toDouble() ?? 0,
      breakdownDiff: diff,
    );
  }
}

class TaxBreakdown {
  final double grossIncome;
  final double deduction;
  final double taxableIncome;
  final double federalTax;
  final double ltcgTax;
  final double stateTax;
  final double ficaTax;
  final double amt;
  final double niit;
  final double totalTax;
  final double effectiveRate;

  const TaxBreakdown({
    this.grossIncome = 0,
    this.deduction = 0,
    this.taxableIncome = 0,
    this.federalTax = 0,
    this.ltcgTax = 0,
    this.stateTax = 0,
    this.ficaTax = 0,
    this.amt = 0,
    this.niit = 0,
    this.totalTax = 0,
    this.effectiveRate = 0,
  });

  factory TaxBreakdown.fromJson(Map<String, dynamic> json) {
    return TaxBreakdown(
      grossIncome: (json['gross_income'] as num?)?.toDouble() ?? 0,
      deduction: (json['deduction'] as num?)?.toDouble() ?? 0,
      taxableIncome: (json['taxable_income'] as num?)?.toDouble() ?? 0,
      federalTax: (json['federal_tax'] as num?)?.toDouble() ?? 0,
      ltcgTax: (json['ltcg_tax'] as num?)?.toDouble() ?? 0,
      stateTax: (json['state_tax'] as num?)?.toDouble() ?? 0,
      ficaTax: (json['fica_tax'] as num?)?.toDouble() ?? 0,
      amt: (json['amt'] as num?)?.toDouble() ?? 0,
      niit: (json['niit'] as num?)?.toDouble() ?? 0,
      totalTax: (json['total_tax'] as num?)?.toDouble() ?? 0,
      effectiveRate: (json['effective_rate'] as num?)?.toDouble() ?? 0,
    );
  }
}

class ScenarioResultData {
  final String name;
  final double totalTax;
  final double effectiveRate;
  final TaxBreakdown? breakdown;

  const ScenarioResultData({
    required this.name,
    required this.totalTax,
    required this.effectiveRate,
    this.breakdown,
  });

  factory ScenarioResultData.fromJson(Map<String, dynamic> json) {
    return ScenarioResultData(
      name: json['name'] as String? ?? '',
      totalTax: (json['total_tax'] as num?)?.toDouble() ?? 0,
      effectiveRate: (json['effective_rate'] as num?)?.toDouble() ?? 0,
      breakdown: json['breakdown'] != null
          ? TaxBreakdown.fromJson(json['breakdown'] as Map<String, dynamic>)
          : null,
    );
  }
}
