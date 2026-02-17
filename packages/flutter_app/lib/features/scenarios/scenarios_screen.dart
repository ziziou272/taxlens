import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'scenarios_provider.dart';
import '../../core/api/api_client.dart' as api;
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_theme.dart';

/// Friendly scenario config — user-facing labels, no jargon.
class _ScenarioConfig {
  final String friendlyName;
  final String question;
  final String description;
  final IconData icon;
  final String paramLabel;
  final String paramHint;
  final double defaultValue;
  final double min;
  final double max;
  final int divisions;
  final String? dropdownLabel;
  final List<String>? dropdownOptions;

  const _ScenarioConfig({
    required this.friendlyName,
    required this.question,
    required this.description,
    required this.icon,
    required this.paramLabel,
    this.paramHint = '',
    this.defaultValue = 50000,
    this.min = 0,
    this.max = 500000,
    this.divisions = 100,
    this.dropdownLabel,
    this.dropdownOptions,
  });
}

const _scenarioConfigs = <String, _ScenarioConfig>{
  'state_move': _ScenarioConfig(
    friendlyName: 'Move to another state',
    question: 'What if I moved?',
    description: 'See how much you\'d save (or pay more) by living in a different state.',
    icon: Icons.flight_takeoff,
    paramLabel: 'Your annual income',
    paramHint: 'We\'ll compare tax in your current state vs. the new one',
    defaultValue: 200000,
    max: 1000000,
    divisions: 200,
    dropdownLabel: 'Move to which state?',
    dropdownOptions: [
      'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
      'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA',
      'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE',
      'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
      'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY',
    ],
  ),
  'capital_gains': _ScenarioConfig(
    friendlyName: 'Sell some investments',
    question: 'What if I sold stocks?',
    description: 'See how much tax you\'d owe on investment gains.',
    icon: Icons.show_chart,
    paramLabel: 'Profit from selling',
    paramHint: 'How much profit would you make (not the total sale, just the gain)',
    defaultValue: 50000,
    max: 500000,
  ),
  'bonus_timing': _ScenarioConfig(
    friendlyName: 'Defer my bonus',
    question: 'What if I got my bonus next year?',
    description: 'Sometimes pushing a bonus to January saves tax by keeping you in a lower bracket this year.',
    icon: Icons.card_giftcard,
    paramLabel: 'Bonus amount',
    paramHint: 'The bonus you\'re thinking of deferring',
    defaultValue: 25000,
    max: 200000,
  ),
  'rsu_timing': _ScenarioConfig(
    friendlyName: 'My stock is about to vest',
    question: 'What if my RSUs vest this year?',
    description: 'When company stock vests, it counts as income. See the tax impact.',
    icon: Icons.schedule,
    paramLabel: 'RSU value at vesting',
    paramHint: 'The dollar value of shares when they vest',
    defaultValue: 50000,
    max: 500000,
  ),
  'iso_exercise': _ScenarioConfig(
    friendlyName: 'Exercise stock options',
    question: 'What if I exercise my options?',
    description: 'Exercising ISOs can trigger extra tax (AMT). See how much.',
    icon: Icons.trending_up,
    paramLabel: 'Value of shares at exercise',
    paramHint: 'Fair market value when you exercise',
    defaultValue: 100000,
    max: 1000000,
    divisions: 200,
  ),
  'income_shift': _ScenarioConfig(
    friendlyName: 'Earn more (or less) next year',
    question: 'What if my income changes?',
    description: 'See how a raise, side hustle, or income change affects your tax.',
    icon: Icons.swap_horiz,
    paramLabel: 'Income change',
    paramHint: 'How much more (or less) you\'d earn',
    defaultValue: 30000,
    max: 300000,
  ),
  'custom': _ScenarioConfig(
    friendlyName: 'Something else',
    question: 'Custom scenario',
    description: 'Adjust deductions or income to see the tax impact.',
    icon: Icons.tune,
    paramLabel: 'Amount',
    paramHint: 'Custom deduction or income adjustment',
    defaultValue: 20000,
    max: 500000,
  ),
};

_ScenarioConfig _getConfig(String typeId) =>
    _scenarioConfigs[typeId] ??
    const _ScenarioConfig(
      friendlyName: 'Scenario',
      question: 'What if...?',
      description: '',
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
  String? _selectedType; // null = show picker
  double _paramValue = 200000;
  String _selectedState = 'WA';
  bool _showBreakdown = false;

  void _selectScenario(String typeId) {
    setState(() {
      _selectedType = typeId;
      _paramValue = _getConfig(typeId).defaultValue;
    });
  }

  void _backToPicker() {
    setState(() => _selectedType = null);
  }

  @override
  Widget build(BuildContext context) {
    final resultAsync = ref.watch(scenarioResultProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('What If...'),
        centerTitle: true,
        leading: _selectedType != null
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: _backToPicker,
              )
            : null,
      ),
      body: _selectedType == null
          ? _buildScenarioPicker(context)
          : _buildScenarioDetail(context, resultAsync),
    );
  }

  /// Friendly scenario picker — question-based cards
  Widget _buildScenarioPicker(BuildContext context) {
    final typesAsync = ref.watch(scenarioTypesProvider);

    return typesAsync.when(
      data: (types) {
        // Use the order from our friendly configs, falling back to API order
        final orderedIds = _scenarioConfigs.keys
            .where((id) => types.any((t) => t.typeId == id))
            .toList();

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('Explore how life changes affect your taxes',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    )),
            const SizedBox(height: 20),
            ...orderedIds.map((typeId) {
              final config = _getConfig(typeId);
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Card(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () => _selectScenario(typeId),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(12),
                              color: AppColors.brand.withAlpha(20),
                            ),
                            child: Icon(config.icon,
                                color: AppColors.brand, size: 24),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(config.question,
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleSmall
                                        ?.copyWith(
                                            fontWeight: FontWeight.bold)),
                                const SizedBox(height: 4),
                                Text(config.description,
                                    style: Theme.of(context)
                                        .textTheme
                                        .bodySmall
                                        ?.copyWith(
                                            color: AppColors.textSecondary)),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          const Icon(Icons.chevron_right,
                              color: AppColors.textSecondary),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }),
          ],
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Text('Failed to load scenarios: $e',
              style: const TextStyle(color: AppColors.negative)),
        ),
      ),
    );
  }

  /// Scenario detail — simplified parameter input
  Widget _buildScenarioDetail(
      BuildContext context, AsyncValue<api.ScenarioComparison?> resultAsync) {
    final config = _getConfig(_selectedType!);
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header
        Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: AppColors.brand.withAlpha(20),
              ),
              child: Icon(config.icon, color: AppColors.brand, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(config.question,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          )),
                  if (config.description.isNotEmpty)
                    Text(config.description,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppColors.textSecondary,
                            )),
                ],
              ),
            ),
          ],
        ),

        const SizedBox(height: 24),

        // State dropdown (for state_move)
        if (config.dropdownOptions != null) ...[
          Text(config.dropdownLabel ?? 'Select',
              style: const TextStyle(fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              contentPadding:
                  EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            ),
            value: _selectedState,
            items: config.dropdownOptions!
                .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                .toList(),
            onChanged: (v) => setState(() => _selectedState = v!),
          ),
          const SizedBox(height: 20),
        ],

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
                  fontSize: 18,
                )),
          ],
        ),
        if (config.paramHint.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 4, bottom: 8),
            child: Text(config.paramHint,
                style: const TextStyle(
                    fontSize: 12, color: AppColors.textSecondary)),
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
                style: const TextStyle(
                    fontSize: 11, color: AppColors.textSecondary)),
            Text(fmt.format(config.max),
                style: const TextStyle(
                    fontSize: 11, color: AppColors.textSecondary)),
          ],
        ),

        const SizedBox(height: 24),

        // Run button
        SizedBox(
          height: 52,
          child: FilledButton.icon(
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.brand,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14)),
            ),
            onPressed: resultAsync.isLoading ? null : _runScenario,
            icon: resultAsync.isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.play_arrow_rounded),
            label: Text(
              resultAsync.isLoading ? 'Calculating...' : 'See the difference',
              style:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
        ),

        const SizedBox(height: 24),

        // Results
        if (resultAsync.hasError)
          _ErrorCard(error: resultAsync.error.toString()),

        if (resultAsync.hasValue && resultAsync.value != null)
          _ResultsSection(
            comparison: resultAsync.value!,
            showBreakdown: _showBreakdown,
            onToggleBreakdown: () =>
                setState(() => _showBreakdown = !_showBreakdown),
          ),
      ],
    );
  }

  void _runScenario() {
    final overrides = <String, dynamic>{};

    switch (_selectedType) {
      case 'state_move':
        overrides['state'] = _selectedState;
        break;
      case 'rsu_timing':
        overrides['rsu_income'] = 0.0;
        break;
      case 'iso_exercise':
        overrides['rsu_income'] = _paramValue;
        break;
      case 'bonus_timing':
        overrides['wages'] = (_paramValue * -1);
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
          scenarioType: _selectedType!,
          alternativeOverrides: overrides,
        );
  }
}

// ─── Result Widgets (unchanged logic, friendlier labels) ───

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
          Expanded(
              child: Text(error,
                  style: const TextStyle(color: AppColors.negative))),
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
    final deltaLabel = isSaving ? 'You\'d save' : 'You\'d pay more';

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
                    style: TextStyle(
                        color: deltaColor,
                        fontSize: 14,
                        fontWeight: FontWeight.w500)),
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
                  '${comparison.savingsPercentage.abs().toStringAsFixed(1)}% ${isSaving ? "less tax" : "more tax"}',
                  style: TextStyle(
                      color: deltaColor.withAlpha(180), fontSize: 13),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 12),

        // Side-by-side
        Row(
          children: [
            Expanded(
              child: _TaxSummaryCard(
                label: 'Now',
                totalTax: comparison.baseline.totalTax,
                effectiveRate: comparison.baseline.effectiveRate,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _TaxSummaryCard(
                label: 'After change',
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
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  dense: true,
                  title: const Text('Detailed breakdown',
                      style: TextStyle(fontWeight: FontWeight.w600)),
                  trailing: Icon(
                      showBreakdown ? Icons.expand_less : Icons.expand_more),
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
                style: TextStyle(
                    color: color, fontWeight: FontWeight.w600, fontSize: 13)),
            const SizedBox(height: 8),
            Text(fmt.format(totalTax),
                style: AppTheme.mono
                    .copyWith(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('${effectiveRate.toStringAsFixed(1)}% avg rate',
                style: const TextStyle(
                    color: AppColors.textSecondary, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _BreakdownTable extends StatelessWidget {
  const _BreakdownTable(
      {required this.baseline, this.alternative, this.diff = const {}});
  final api.TaxBreakdown baseline;
  final api.TaxBreakdown? alternative;
  final Map<String, double> diff;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
    final rows = <_BreakdownRow>[
      _BreakdownRow(
          'Federal', baseline.federalTax, alternative?.federalTax, diff['federal_tax']),
      _BreakdownRow(
          'State', baseline.stateTax, alternative?.stateTax, diff['state_tax']),
      _BreakdownRow(
          'Investment gains', baseline.ltcgTax, alternative?.ltcgTax, null),
      _BreakdownRow(
          'Social Security & Medicare', baseline.ficaTax, alternative?.ficaTax, diff['fica_tax']),
      _BreakdownRow(
          'Alt. minimum tax', baseline.amt, alternative?.amt, diff['amt']),
      _BreakdownRow('Investment surtax', baseline.niit, alternative?.niit,
          diff['niit']),
    ];

    return Table(
      columnWidths: const {
        0: FlexColumnWidth(2.2),
        1: FlexColumnWidth(1.3),
        2: FlexColumnWidth(1.3),
        3: FlexColumnWidth(1.3),
      },
      children: [
        TableRow(
          children: [
            const Text('',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
            Text('Now',
                style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                    color: AppColors.textSecondary),
                textAlign: TextAlign.right),
            Text('After',
                style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                    color: AppColors.brand),
                textAlign: TextAlign.right),
            Text('Δ',
                style: const TextStyle(
                    fontWeight: FontWeight.w600, fontSize: 12),
                textAlign: TextAlign.right),
          ],
        ),
        ...rows
            .where((r) => r.baseline != 0 || (r.alternative ?? 0) != 0)
            .map((r) {
          final delta = r.delta ?? ((r.alternative ?? 0) - r.baseline);
          final deltaColor = delta < 0
              ? AppColors.positive
              : (delta > 0 ? AppColors.negative : AppColors.textSecondary);
          return TableRow(
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(r.label, style: const TextStyle(fontSize: 13)),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(fmt.format(r.baseline),
                    style: AppTheme.mono.copyWith(fontSize: 12),
                    textAlign: TextAlign.right),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(fmt.format(r.alternative ?? 0),
                    style: AppTheme.mono
                        .copyWith(fontSize: 12, color: AppColors.brand),
                    textAlign: TextAlign.right),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(
                  '${delta >= 0 ? "+" : ""}${fmt.format(delta)}',
                  style: AppTheme.mono.copyWith(
                      fontSize: 12,
                      color: deltaColor,
                      fontWeight: FontWeight.w600),
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
