import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'scenarios_provider.dart';
import 'widgets/scenario_comparison.dart';

class ScenariosScreen extends ConsumerWidget {
  const ScenariosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scenarios = ref.watch(scenariosProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('What-If Scenarios')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'Scenario Type',
              border: OutlineInputBorder(),
            ),
            value: 'all',
            items: const [
              DropdownMenuItem(value: 'all', child: Text('All Scenarios')),
              DropdownMenuItem(
                  value: 'retirement', child: Text('Retirement')),
              DropdownMenuItem(
                  value: 'investment', child: Text('Investment')),
              DropdownMenuItem(
                  value: 'deduction', child: Text('Deductions')),
            ],
            onChanged: (_) {},
          ),
          const SizedBox(height: 16),
          ...scenarios.map((s) => ScenarioComparison(scenario: s)),
        ],
      ),
    );
  }
}
