import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'scenarios_provider.dart';
import 'widgets/scenario_comparison.dart';
import '../../core/api/api_client.dart' as api_models;
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_theme.dart';

class ScenariosScreen extends ConsumerStatefulWidget {
  const ScenariosScreen({super.key});

  @override
  ConsumerState<ScenariosScreen> createState() => _ScenariosScreenState();
}

class _ScenariosScreenState extends ConsumerState<ScenariosScreen> {
  String _selectedType = 'retirement';
  final _paramController = TextEditingController(text: '23500');

  @override
  void dispose() {
    _paramController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final typesAsync = ref.watch(scenarioTypesProvider);
    final resultAsync = ref.watch(scenarioResultProvider);
    final scenarios = ref.watch(scenariosProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('What-If Scenarios')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          typesAsync.when(
            data: (types) => DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'Scenario Type',
                border: OutlineInputBorder(),
              ),
              value: types.any((t) => t.typeId == _selectedType)
                  ? _selectedType
                  : (types.isNotEmpty ? types.first.typeId : null),
              items: types
                  .map((t) => DropdownMenuItem(
                      value: t.typeId, child: Text(t.name)))
                  .toList(),
              onChanged: (v) => setState(() => _selectedType = v!),
            ),
            loading: () => const LinearProgressIndicator(),
            error: (e, _) => Text('Failed to load types: $e'),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _paramController,
            decoration: const InputDecoration(
              labelText: 'Amount / Parameter',
              prefixText: '\$ ',
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: resultAsync.isLoading
                ? null
                : () {
                    final amount =
                        double.tryParse(_paramController.text) ?? 0;
                    ref
                        .read(scenarioResultProvider.notifier)
                        .runComparison(
                          scenarioType: _selectedType,
                          alternativeOverrides: {
                            'itemized_deductions': amount,
                          },
                        );
                  },
            icon: resultAsync.isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.compare_arrows),
            label: Text(resultAsync.isLoading ? 'Running...' : 'Run Scenario'),
          ),
          const SizedBox(height: 24),
          if (resultAsync.hasError)
            Card(
              color: Colors.red.withAlpha(30),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Error: ${resultAsync.error}'),
              ),
            ),
          ...scenarios.map((s) => ScenarioComparison(scenario: s)),
          if (resultAsync.hasValue && resultAsync.value != null) ...[
            const Divider(height: 32),
            _ComparisonDetail(comparison: resultAsync.value!),
          ],
        ],
      ),
    );
  }
}

class _ComparisonDetail extends StatelessWidget {
  const _ComparisonDetail({required this.comparison});
  final api_models.ScenarioComparison comparison;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Comparison Detail',
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _Row('Baseline Tax', fmt.format(comparison.baseline.totalTax)),
            _Row('Alternative Tax', fmt.format(comparison.alternative.totalTax)),
            const Divider(),
            _Row(
              'Tax Savings',
              fmt.format(comparison.taxSavings),
              valueColor: AppColors.positive,
            ),
            _Row(
              'Savings %',
              '${comparison.savingsPercentage.toStringAsFixed(1)}%',
              valueColor: AppColors.positive,
            ),
          ],
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row(this.label, this.value, {this.valueColor});
  final String label;
  final String value;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(value,
              style: AppTheme.mono.copyWith(
                fontWeight: FontWeight.w600,
                color: valueColor,
              )),
        ],
      ),
    );
  }
}
