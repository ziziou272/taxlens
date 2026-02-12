import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:taxlens_app/core/api/api_client.dart';
import 'package:taxlens_app/core/api/api_endpoints.dart';

void main() {
  late ApiClient apiClient;
  late DioAdapter dioAdapter;

  setUp(() {
    apiClient = ApiClient(baseUrl: 'http://localhost:8100');
    dioAdapter = DioAdapter(dio: apiClient.dio);
  });

  group('calculateTax', () {
    const input = TaxInput(
      filingStatus: 'single',
      wages: 150000,
      rsuIncome: 50000,
      state: 'CA',
      federalWithheld: 30000,
      stateWithheld: 10000,
    );

    test('returns parsed TaxResult on success', () async {
      dioAdapter.onPost(
        ApiEndpoints.calculate,
        (server) => server.reply(200, {
          'total_income': 200000.0,
          'federal_tax': 35000.0,
          'state_tax': 12000.0,
          'total_tax': 47000.0,
          'effective_rate': 23.5,
          'marginal_rate': 32.0,
          'balance_due': 7000.0,
          'taxable_income': 186050.0,
          'deduction_used': 13950.0,
          'social_security_tax': 9932.0,
          'medicare_tax': 2900.0,
        }),
        data: input.toJson(),
      );

      final result = await apiClient.calculateTax(input);

      expect(result.totalIncome, 200000.0);
      expect(result.federalTax, 35000.0);
      expect(result.stateTax, 12000.0);
      expect(result.totalTax, 47000.0);
      expect(result.effectiveRate, 23.5);
      expect(result.marginalRate, 32.0);
    });

    test('throws ApiException on timeout', () async {
      dioAdapter.onPost(
        ApiEndpoints.calculate,
        (server) => server.throws(
          0,
          DioException(
            type: DioExceptionType.connectionTimeout,
            requestOptions: RequestOptions(path: ApiEndpoints.calculate),
          ),
        ),
        data: input.toJson(),
      );

      expect(
        () => apiClient.calculateTax(input),
        throwsA(isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('timed out'),
        )),
      );
    });

    test('throws ApiException on 500 error', () async {
      dioAdapter.onPost(
        ApiEndpoints.calculate,
        (server) => server.throws(
          500,
          DioException(
            type: DioExceptionType.badResponse,
            response: Response(
              statusCode: 500,
              requestOptions: RequestOptions(path: ApiEndpoints.calculate),
              data: {'detail': 'Internal error'},
            ),
            requestOptions: RequestOptions(path: ApiEndpoints.calculate),
          ),
        ),
        data: input.toJson(),
      );

      expect(
        () => apiClient.calculateTax(input),
        throwsA(isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('Server error'),
        )),
      );
    });

    test('throws ApiException on network error', () async {
      dioAdapter.onPost(
        ApiEndpoints.calculate,
        (server) => server.throws(
          0,
          DioException(
            type: DioExceptionType.connectionError,
            requestOptions: RequestOptions(path: ApiEndpoints.calculate),
          ),
        ),
        data: input.toJson(),
      );

      expect(
        () => apiClient.calculateTax(input),
        throwsA(isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('Cannot connect'),
        )),
      );
    });
  });

  group('TaxInput', () {
    test('toJson produces correct keys', () {
      const input = TaxInput(
        filingStatus: 'married_jointly',
        wages: 100000,
        rsuIncome: 25000,
        state: 'NY',
      );
      final json = input.toJson();
      expect(json['filing_status'], 'married_jointly');
      expect(json['wages'], 100000);
      expect(json['rsu_income'], 25000);
      expect(json['state'], 'NY');
    });
  });
}
