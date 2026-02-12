import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';

class IncomeBreakdownChart extends StatelessWidget {
  const IncomeBreakdownChart({super.key, required this.breakdown});

  final Map<String, double> breakdown;

  static const _colors = [
    AppColors.brand,
    AppColors.info,
    AppColors.warning,
    AppColors.positive,
  ];

  @override
  Widget build(BuildContext context) {
    final total = breakdown.values.fold(0.0, (a, b) => a + b);
    final entries = breakdown.entries.toList();
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Income Breakdown',
                style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 16),
            SizedBox(
              height: 180,
              child: PieChart(
                PieChartData(
                  sectionsSpace: 2,
                  centerSpaceRadius: 40,
                  sections: List.generate(entries.length, (i) {
                    final pct = entries[i].value / total * 100;
                    return PieChartSectionData(
                      value: entries[i].value,
                      color: _colors[i % _colors.length],
                      radius: 50,
                      title: '${pct.toStringAsFixed(0)}%',
                      titleStyle: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.white),
                    );
                  }),
                ),
              ),
            ),
            const SizedBox(height: 12),
            ...List.generate(entries.length, (i) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    Container(
                        width: 12,
                        height: 12,
                        color: _colors[i % _colors.length]),
                    const SizedBox(width: 8),
                    Expanded(child: Text(entries[i].key)),
                    Text(fmt.format(entries[i].value)),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
