class ApiEndpoints {
  ApiEndpoints._();

  static const calculate = '/api/tax/calculate';
  static const withholdingGap = '/api/tax/withholding-gap';
  static const alertsCheck = '/api/alerts/check';
  static const scenarioTypes = '/api/scenarios/types';
  static const scenarioRun = '/api/scenarios/run';
  static const health = '/api/health';

  // Tax Returns (prior year import)
  static const taxReturnUploadPdf = '/api/tax-returns/upload-pdf';
  static const taxReturnConfirm = '/api/tax-returns/confirm';
  static const taxReturns = '/api/tax-returns';
  static String taxReturnYear(int year) => '/api/tax-returns/$year';
}
