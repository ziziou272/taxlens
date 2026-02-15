import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'scenarios_provider.dart';
import '../../core/api/api_client.dart' as api;
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_theme.dart';

/// Scenario-specific configuration for the UI.
class _ScenarioConfig {
  final String label;
  final IconData icon;
  final String paramLabel;
  final String paramHint;
  final double defaultValue;
  final double min;
  final double max;
  final int divisions;
  final String? secondaryParam;
  final List<String>? dropdownOptions;
  final String? dropdownLabel;

  const _ScenarioConfig({
    required this.label,
    required this.icon,
    required this.paramLabel,
    this.paramHint = '',
    this.defaultValue = 50000,
    this.min = 0,
    this.max = 500000,
    this.divisions = 100,
    this.secondaryParam,
    this.dropdownOptions,
    this.dropdownLabel,
  });
}

const _scenarioConfigs = <String, _ScenarioConfig>{
  'rsu_timing': _ScenarioConfig(
    label: 'RSU Vesting Timing',
    icon: Icons.schedule,
    paramLabel: 'RSU Income to Defer',
    paramHint: 'Amount of RSU income to shift to next year',
    defaultValue: 50000,
    max: 500000,
  ),
  'iso_exercise': _ScenarioConfig(
    label: 'ISO Exercise',
    icon: Icons.trending_up,
    paramLabel: 'ISO Exercise Value',
    paramHint: 'Fair market value of shares at exercise',
    defaultValue: 100000,
    max: 1000000,
    divisions: 200,
  ),
  'bonus_timing': _ScenarioConfig(
    label: 'Bonus Timing',
    icon: Icons.card_giftcard,
    paramLabel: 'Bonus Amount to Defer',
    paramHint: 'Bonus to defer to next tax year',
    defaultValue: 25000,
    max: 200000,
  ),
  'state_move': _ScenarioConfig(
    label: 'State Residency Change',
    icon: Icons.flight_takeoff,
    paramLabel: 'Income',
    paramHint: 'Your total income for comparison',
    defaultValue: 200000,
    max: 1000000,
    divisions: 200,
    dropdownLabel: 'Move to State',
    dropdownOptions: [
      'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
      'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA',
      'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE',
      'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
      'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY',
    ],
  ),
  'capital_gains': _ScenarioConfig(
    label: 'Capital Gains Timing',
    icon: Icons.show_chart,
    paramLabel: 'Gains to Realize',
    paramHint: 'Long-term capital gains to realize now',
    defaultValue: 50000,
    max: 500000,
  ),
  'income_shift': _ScenarioConfig(
    label: 'Income Shifting',
    icon: Icons.swap_horiz,
    paramLabel: 'Income to Shift',
    paramHint: 'Amount of income to shift between years',
    defaultValue: 30000,
    max: 300000,
  ),
  'custom': _ScenarioConfig(
    label: 'Custom Scenario',
    icon: Icons.tune,
    paramLabel: 'Custom Amount',
    paramHint: 'Adjust the deduction or income amount',
    defaultValue: 20000,
    max: 500000,
  ),
};

_ScenarioConfig _getConfig(String typeId) =>
    _scenarioConfigs[typeId] ??
    const _ScenarioConfig(
      label: 'Scenario',
      icon: Icons.compare_arrows,
      paramLabel: 'Amount',
      defaultValue: 50000,
    );

class ScenariosScreen extends ConsumerStatefulWidget {
  const ScenariosScreen({super.key});

  @override
  ConsumerState<ScenariosScreen> createState() => _ScenariosScreenState();
}

class _ScenariosScreenState extends ConsumerState<ScenariosScreen> {
  String _selectedType = 'state_move';
  double _paramValue = 200000;
  String _selectedState = 'WA';
  bool _showBreakdown = false;

  @override
  Widget build(BuildContext context) {
    final typesAsync = ref.watch(scenarioTypesProvider);
    final resultAsync = ref.watch(scenarioResultProvider);
    final config = _getConfig(_selectedType);
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('What-If Scenarios'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // --- Scenario Picker ---
          _SectionCard(
            icon: Icons.category,
            title: 'Choose Scenario',
            child: typesAsync.when(
              data: (types) {
                if (!types.any((t) => t.typeId == _selectedType) && types.isNotEmpty) {
                  _selectedType = types.first.typeId;
                }
                return Column(
                  children: types.map((t) {
                    final c = _getConfig(t.typeId);
                    final selected = t.typeId == _selectedType;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Material(
                        color: selected
                            ? AppColors.brand.withAlpha(40)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(12),
                        child: ListTile(
                          dense: true,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: BorderSide(
                              color: selected ? AppColors.brand : Colors.white12,
                            ),
                          ),
                          leading: Icon(c.icon,
                              color: selected ? AppColors.brand : AppColors.textSecondary),
                          title: Text(t.name,
                              style: TextStyle(
                                fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                                color: selected ? AppColors.brand : null,
                              )),
                          subtitle: Text(t.description,
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                          trailing: selected
                              ? const Icon(Icons.check_circle, color: AppColors.brand, size: 20)
                              : null,
                          onTap: () => setState(() {
                            _selectedType = t.typeId;
                            _paramValue = _getConfig(t.typeId).defaultValue;
                          }),
                        ),
                      ),
                    );
                  }).toList(),
                );
              },
              loading: () => const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (e, _) => Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Failed to load: $e',
                    style: const TextStyle(color: AppColors.negative)),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // --- Parameters ---
          _SectionCard(
            icon: config.icon,
            title: config.label,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (config.paramHint.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(config.paramHint,
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                  ),

                // Amount slider
                Row(
                  children: [
                    Text(config.paramLabel,
                        style: const TextStyle(fontWeight: FontWeight.w500)),
                    const Spacer(),
                    Text(fmt.format(_paramValue),
                        style: AppTheme.mono.copyWith(
                          color: AppColors.brand,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        )),
                  ],
                ),
                SliderTheme(
                  data: SliderThemeData(
                    activeTrackColor: AppColors.brand,
                    thumbColor: AppColors.brand,
                    inactiveTrackColor: AppColors.brand.withAlpha(40),
                    overlayColor: AppColors.brand.withAlpha(30),
                  ),
                  child: Slider(
                    value: _paramValue.clamp(config.min, config.max),
                    min: config.min,
                    max: config.max,
                    divisions: config.divisions,
                    onChanged: (v) => setState(() => _paramValue = v),
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(fmt.format(config.min),
                        style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                    Text(fmt.format(config.max),
                        style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                  ],
                ),

                // State dropdown for state_move
                if (config.dropdownOptions != null) ...[
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      labelText: config.dropdownLabel ?? 'Select',
                      border: const OutlineInputBorder(),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    value: _selectedState,
                    items: config.dropdownOptions!
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _selectedState = v!),
                  ),
                ],
              ],
            ),
          ),

          const SizedBox(height: 16),

          // --- Run Button ---
          SizedBox(
            height: 52,
            child: FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.brand,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              onPressed: resultAsync.isLoading
                  ? null
                  : () => _runScenario(),
              icon: resultAsync.isLoading
                  ? const SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.play_arrow_rounded),
              label: Text(
                resultAsync.isLoading ? 'Calculating...' : 'Run Comparison',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ),

          const SizedBox(height: 24),

          // --- Results ---
          if (resultAsync.hasError)
            _ErrorCard(error: resultAsync.error.toString()),

          if (resultAsync.hasValue && resultAsync.value != null)
            _ResultsSection(
              comparison: resultAsync.value!,
              showBreakdown: _showBreakdown,
              onToggleBreakdown: () => setState(() => _showBreakdown = !_showBreakdown),
            ),
        ],
      ),
    );
  }

  void _runScenario() {
    final overrides = <String, dynamic>{};

    switch (_selectedType) {
      case 'state_move':
        overrides['state'] = _selectedState;
        break;
      case 'rsu_timing':
        overrides['rsu_income'] = 0.0; // defer all RSU
        break;
      case 'iso_exercise':
        overrides['rsu_income'] = _paramValue;
        break;
      case 'bonus_timing':
        overrides['wages'] = (_paramValue * -1); // reduce wages by bonus amount
        break;
      case 'capital_gains':
        overrides['long_term_gains'] = _paramValue;
        break;
      case 'income_shift':
        overrides['wages'] = _paramValue * -1;
        break;
      case 'custom':
        overrides['itemized_deductions'] = _paramValue;
        break;
    }

    ref.read(scenarioResultProvider.notifier).runComparison(
      scenarioType: _selectedType,
      alternativeOverrides: overrides,
    );
  }
}

// ─── Reusable Widgets ───

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.icon, required this.title, required this.child});
  final IconData icon;
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(icon, size: 20, color: AppColors.brand),
              const SizedBox(width: 8),
              Text(title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      )),
            ]),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.error});
  final String error;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.negative.withAlpha(25),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: AppColors.negative.withAlpha(60)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(children: [
          const Icon(Icons.error_outline, color: AppColors.negative),
          const SizedBox(width: 12),
          Expanded(child: Text(error, style: const TextStyle(color: AppColors.negative))),
        ]),
      ),
    );
  }
}

class _ResultsSection extends StatelessWidget {
  const _ResultsSection({
    required this.comparison,
    required this.showBreakdown,
    required this.onToggleBreakdown,
  });
  final api.ScenarioComparison comparison;
  final bool showBreakdown;
  final VoidCallback onToggleBreakdown;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    final isSaving = comparison.taxSavings > 0;
    final deltaColor = isSaving ? AppColors.positive : AppColors.negative;
    final deltaIcon = isSaving ? Icons.trending_down : Icons.trending_up;
    final deltaLabel = isSaving ? 'You Save' : 'Extra Tax';

    return Column(
      children: [
        // Delta hero
        Card(
          color: deltaColor.withAlpha(20),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(color: deltaColor.withAlpha(80)),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 20),
            child: Column(
              children: [
                Icon(deltaIcon, color: deltaColor, size: 36),
                const SizedBox(height: 8),
                Text(deltaLabel,
                    style: TextStyle(color: deltaColor, fontSize: 14, fontWeight: FontWeight.w500)),
                const SizedBox(height: 4),
                Text(
                  fmt.format(comparison.taxSavings.abs()),
                  style: AppTheme.mono.copyWith(
                    color: deltaColor,
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${comparison.savingsPercentage.abs().toStringAsFixed(1)}% ${isSaving ? "reduction" : "increase"}',
                  style: TextStyle(color: deltaColor.withAlpha(180), fontSize: 13),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 12),

        // Side-by-side comparison
        Row(
          children: [
            Expanded(
              child: _TaxSummaryCard(
                label: comparison.baseline.name.isEmpty ? 'Current' : comparison.baseline.name,
                totalTax: comparison.baseline.totalTax,
                effectiveRate: comparison.baseline.effectiveRate,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _TaxSummaryCard(
                label: comparison.alternative.name.isEmpty ? 'Alternative' : comparison.alternative.name,
                totalTax: comparison.alternative.totalTax,
                effectiveRate: comparison.alternative.effectiveRate,
                color: AppColors.brand,
              ),
            ),
          ],
        ),

        const SizedBox(height: 12),

        // Breakdown toggle
        if (comparison.baseline.breakdown != null)
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  dense: true,
                  title: const Text('Tax Breakdown', style: TextStyle(fontWeight: FontWeight.w600)),
                  trailing: Icon(showBreakdown ? Icons.expand_less : Icons.expand_more),
                  onTap: onToggleBreakdown,
                ),
                if (showBreakdown) ...[
                  const Divider(height: 1),
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: _BreakdownTable(
                      baseline: comparison.baseline.breakdown!,
                      alternative: comparison.alternative.breakdown,
                      diff: comparison.breakdownDiff,
                    ),
                  ),
                ],
              ],
            ),
          ),
      ],
    );
  }
}

class _TaxSummaryCard extends StatelessWidget {
  const _TaxSummaryCard({
    required this.label,
    required this.totalTax,
    required this.effectiveRate,
    required this.color,
  });
  final String label;
  final double totalTax;
  final double effectiveRate;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: color.withAlpha(60)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(label,
                style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 13)),
            const SizedBox(height: 8),
            Text(fmt.format(totalTax),
                style: AppTheme.mono.copyWith(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('${effectiveRate.toStringAsFixed(1)}% effective',
                style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _BreakdownTable extends StatelessWidget {
  const _BreakdownTable({required this.baseline, this.alternative, this.diff = const {}});
  final api.TaxBreakdown baseline;
  final api.TaxBreakdown? alternative;
  final Map<String, double> diff;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    final rows = <_BreakdownRow>[
      _BreakdownRow('Federal Tax', baseline.federalTax, alternative?.federalTax, diff['federal_tax']),
      _BreakdownRow('State Tax', baseline.stateTax, alternative?.stateTax, diff['state_tax']),
      _BreakdownRow('LTCG Tax', baseline.ltcgTax, alternative?.ltcgTax, null),
      _BreakdownRow('FICA', baseline.ficaTax, alternative?.ficaTax, diff['fica_tax']),
      _BreakdownRow('AMT', baseline.amt, alternative?.amt, diff['amt']),
      _BreakdownRow('NIIT', baseline.niit, alternative?.niit, diff['niit']),
    ];

    return Table(
      columnWidths: const {
        0: FlexColumnWidth(2),
        1: FlexColumnWidth(1.5),
        2: FlexColumnWidth(1.5),
        3: FlexColumnWidth(1.5),
      },
      children: [
        TableRow(
          children: [
            const Text('', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
            Text('Current', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary), textAlign: TextAlign.right),
            Text('Alt', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.brand), textAlign: TextAlign.right),
            Text('Δ', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12), textAlign: TextAlign.right),
          ],
        ),
        ...rows.where((r) => r.baseline != 0 || (r.alternative ?? 0) != 0).map((r) {
          final delta = r.delta ?? ((r.alternative ?? 0) - r.baseline);
          final deltaColor = delta < 0 ? AppColors.positive : (delta > 0 ? AppColors.negative : AppColors.textSecondary);
          return TableRow(
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(r.label, style: const TextStyle(fontSize: 13)),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(fmt.format(r.baseline), style: AppTheme.mono.copyWith(fontSize: 12), textAlign: TextAlign.right),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(fmt.format(r.alternative ?? 0), style: AppTheme.mono.copyWith(fontSize: 12, color: AppColors.brand), textAlign: TextAlign.right),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(
                  '${delta >= 0 ? "+" : ""}${fmt.format(delta)}',
                  style: AppTheme.mono.copyWith(fontSize: 12, color: deltaColor, fontWeight: FontWeight.w600),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          );
        }),
      ],
    );
  }
}

class _BreakdownRow {
  final String label;
  final double baseline;
  final double? alternative;
  final double? delta;
  const _BreakdownRow(this.label, this.baseline, this.alternative, this.delta);
}
