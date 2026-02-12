import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/scenario.dart';

final scenariosProvider = Provider<List<Scenario>>((ref) {
  return const [
    Scenario(
      id: '1',
      name: 'Max 401(k) Contribution',
      type: 'retirement',
      currentTax: 70630,
      projectedTax: 66130,
      savings: 4500,
    ),
    Scenario(
      id: '2',
      name: 'Harvest Capital Losses',
      type: 'investment',
      currentTax: 70630,
      projectedTax: 68430,
      savings: 2200,
    ),
    Scenario(
      id: '3',
      name: 'Charitable Donation (\$10k)',
      type: 'deduction',
      currentTax: 70630,
      projectedTax: 67430,
      savings: 3200,
    ),
  ];
});
