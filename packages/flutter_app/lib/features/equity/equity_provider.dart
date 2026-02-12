import 'package:flutter_riverpod/flutter_riverpod.dart';

enum GrantType { rsu, iso, nso, espp }

class TaxLot {
  const TaxLot({
    required this.dateAcquired,
    required this.shares,
    required this.costBasis,
    required this.currentValue,
    required this.holdingPeriodDays,
  });

  final DateTime dateAcquired;
  final int shares;
  final double costBasis;
  final double currentValue;
  final int holdingPeriodDays;

  double get gainLoss => currentValue - costBasis;
  bool get isLongTerm => holdingPeriodDays >= 366;
  int get daysToLongTerm => isLongTerm ? 0 : 366 - holdingPeriodDays;
}

class Holding {
  const Holding({
    required this.id,
    required this.symbol,
    required this.grantType,
    required this.totalShares,
    required this.currentValue,
    required this.costBasis,
    this.grantDate,
    this.exercisePrice,
    this.sharesGranted,
    this.sharesVested,
    this.taxLots = const [],
  });

  final String id;
  final String symbol;
  final GrantType grantType;
  final int totalShares;
  final double currentValue;
  final double costBasis;
  final DateTime? grantDate;
  final double? exercisePrice;
  final int? sharesGranted;
  final int? sharesVested;
  final List<TaxLot> taxLots;

  double get unrealizedGain => currentValue - costBasis;

  String get grantTypeLabel => switch (grantType) {
        GrantType.rsu => 'RSU',
        GrantType.iso => 'ISO',
        GrantType.nso => 'NSO',
        GrantType.espp => 'ESPP',
      };
}

final holdingsProvider = Provider<List<Holding>>((ref) {
  return [
    Holding(
      id: '1',
      symbol: 'ACME',
      grantType: GrantType.rsu,
      totalShares: 500,
      currentValue: 87500.00,
      costBasis: 62000.00,
      grantDate: DateTime(2023, 3, 15),
      sharesGranted: 2000,
      sharesVested: 1000,
      taxLots: [
        TaxLot(
          dateAcquired: DateTime(2024, 3, 15),
          shares: 250,
          costBasis: 30000.00,
          currentValue: 43750.00,
          holdingPeriodDays: 335,
        ),
        TaxLot(
          dateAcquired: DateTime(2024, 9, 15),
          shares: 250,
          costBasis: 32000.00,
          currentValue: 43750.00,
          holdingPeriodDays: 150,
        ),
      ],
    ),
    Holding(
      id: '2',
      symbol: 'ACME',
      grantType: GrantType.iso,
      totalShares: 200,
      currentValue: 35000.00,
      costBasis: 18000.00,
      grantDate: DateTime(2022, 6, 1),
      exercisePrice: 90.00,
      sharesGranted: 1000,
      sharesVested: 500,
      taxLots: [
        TaxLot(
          dateAcquired: DateTime(2023, 12, 1),
          shares: 200,
          costBasis: 18000.00,
          currentValue: 35000.00,
          holdingPeriodDays: 440,
        ),
      ],
    ),
    Holding(
      id: '3',
      symbol: 'ACME',
      grantType: GrantType.espp,
      totalShares: 150,
      currentValue: 26250.00,
      costBasis: 19875.00,
      grantDate: DateTime(2024, 6, 30),
      sharesGranted: 150,
      sharesVested: 150,
      taxLots: [
        TaxLot(
          dateAcquired: DateTime(2024, 6, 30),
          shares: 150,
          costBasis: 19875.00,
          currentValue: 26250.00,
          holdingPeriodDays: 227,
        ),
      ],
    ),
  ];
});

final grantDetailProvider = Provider.family<Holding?, String>((ref, id) {
  final holdings = ref.watch(holdingsProvider);
  try {
    return holdings.firstWhere((h) => h.id == id);
  } catch (_) {
    return null;
  }
});
