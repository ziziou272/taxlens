import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/settings_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/glossary_tooltip.dart';
import '../dashboard_provider.dart';

class TaxInputForm extends ConsumerStatefulWidget {
  const TaxInputForm({super.key});

  @override
  ConsumerState<TaxInputForm> createState() => _TaxInputFormState();
}

class _TaxInputFormState extends ConsumerState<TaxInputForm> {
  final _formKey = GlobalKey<FormState>();
  bool _showDetailed = false;
  bool _showDeductions = false;
  bool _showRetirement = false;
  bool _showFamily = false;

  // Income controllers
  late final TextEditingController _wagesCtrl;
  late final TextEditingController _rsuCtrl;
  late final TextEditingController _stGainsCtrl;
  late final TextEditingController _ltGainsCtrl;
  late final TextEditingController _fedWithheldCtrl;
  late final TextEditingController _stateWithheldCtrl;

  // Deduction controllers
  late final TextEditingController _mortgageCtrl;
  late final TextEditingController _saltCtrl;
  late final TextEditingController _charitableCtrl;
  late final TextEditingController _medicalCtrl;

  // Retirement & Pre-tax controllers
  late final TextEditingController _ctrl401k;
  late final TextEditingController _iraCtrl;
  late final TextEditingController _hsaCtrl;
  late final TextEditingController _studentLoanCtrl;

  // Family & Education controllers
  late final TextEditingController _childrenCtrl;
  late final TextEditingController _otherDependentsCtrl;
  late final TextEditingController _educationExpCtrl;

  // Family state (non-text)
  late String _educationType;
  late bool _ageOver50;

  @override
  void initState() {
    super.initState();
    final s = ref.read(settingsProvider);

    // Income
    _wagesCtrl = TextEditingController(
        text: s.wages > 0 ? s.wages.toStringAsFixed(0) : '');
    _rsuCtrl = TextEditingController(
        text: s.rsuIncome > 0 ? s.rsuIncome.toStringAsFixed(0) : '');
    _stGainsCtrl = TextEditingController(
        text: s.capitalGainsShort > 0
            ? s.capitalGainsShort.toStringAsFixed(0)
            : '');
    _ltGainsCtrl = TextEditingController(
        text: s.capitalGainsLong > 0
            ? s.capitalGainsLong.toStringAsFixed(0)
            : '');
    _fedWithheldCtrl = TextEditingController(
        text: s.federalWithheld > 0
            ? s.federalWithheld.toStringAsFixed(0)
            : '');
    _stateWithheldCtrl = TextEditingController(
        text: s.stateWithheld > 0
            ? s.stateWithheld.toStringAsFixed(0)
            : '');

    // Deductions
    _mortgageCtrl = TextEditingController(
        text: s.mortgageInterest > 0
            ? s.mortgageInterest.toStringAsFixed(0)
            : '');
    _saltCtrl = TextEditingController(
        text: s.saltPaid > 0 ? s.saltPaid.toStringAsFixed(0) : '');
    _charitableCtrl = TextEditingController(
        text: s.charitableContributions > 0
            ? s.charitableContributions.toStringAsFixed(0)
            : '');
    _medicalCtrl = TextEditingController(
        text: s.medicalExpenses > 0
            ? s.medicalExpenses.toStringAsFixed(0)
            : '');

    // Retirement
    _ctrl401k = TextEditingController(
        text: s.contributions401k > 0
            ? s.contributions401k.toStringAsFixed(0)
            : '');
    _iraCtrl = TextEditingController(
        text: s.iraContributions > 0
            ? s.iraContributions.toStringAsFixed(0)
            : '');
    _hsaCtrl = TextEditingController(
        text: s.hsaContributions > 0
            ? s.hsaContributions.toStringAsFixed(0)
            : '');
    _studentLoanCtrl = TextEditingController(
        text: s.studentLoanInterest > 0
            ? s.studentLoanInterest.toStringAsFixed(0)
            : '');

    // Family
    _childrenCtrl = TextEditingController(
        text: s.numChildrenUnder17 > 0
            ? s.numChildrenUnder17.toString()
            : '');
    _otherDependentsCtrl = TextEditingController(
        text: s.numOtherDependents > 0
            ? s.numOtherDependents.toString()
            : '');
    _educationExpCtrl = TextEditingController(
        text: s.educationExpenses > 0
            ? s.educationExpenses.toStringAsFixed(0)
            : '');
    _educationType = s.educationType;
    _ageOver50 = s.ageOver50;

    // Auto-expand sections if user already has fields filled
    if (s.rsuIncome > 0 ||
        s.capitalGainsShort > 0 ||
        s.capitalGainsLong > 0) {
      _showDetailed = true;
    }
    if (s.mortgageInterest > 0 ||
        s.saltPaid > 0 ||
        s.charitableContributions > 0 ||
        s.medicalExpenses > 0) {
      _showDeductions = true;
    }
    if (s.contributions401k > 0 ||
        s.iraContributions > 0 ||
        s.hsaContributions > 0 ||
        s.studentLoanInterest > 0) {
      _showRetirement = true;
    }
    if (s.numChildrenUnder17 > 0 ||
        s.numOtherDependents > 0 ||
        s.educationExpenses > 0 ||
        s.educationType != 'none' ||
        s.ageOver50) {
      _showFamily = true;
    }
  }

  @override
  void dispose() {
    _wagesCtrl.dispose();
    _rsuCtrl.dispose();
    _stGainsCtrl.dispose();
    _ltGainsCtrl.dispose();
    _fedWithheldCtrl.dispose();
    _stateWithheldCtrl.dispose();
    _mortgageCtrl.dispose();
    _saltCtrl.dispose();
    _charitableCtrl.dispose();
    _medicalCtrl.dispose();
    _ctrl401k.dispose();
    _iraCtrl.dispose();
    _hsaCtrl.dispose();
    _studentLoanCtrl.dispose();
    _childrenCtrl.dispose();
    _otherDependentsCtrl.dispose();
    _educationExpCtrl.dispose();
    super.dispose();
  }

  void _calculate() {
    if (!_formKey.currentState!.validate()) return;

    final notifier = ref.read(settingsProvider.notifier);

    // Income
    notifier.setWages(double.tryParse(_wagesCtrl.text) ?? 0);
    notifier.setFederalWithheld(double.tryParse(_fedWithheldCtrl.text) ?? 0);
    notifier.setStateWithheld(double.tryParse(_stateWithheldCtrl.text) ?? 0);

    if (_showDetailed) {
      notifier.setRsuIncome(double.tryParse(_rsuCtrl.text) ?? 0);
      notifier.setCapitalGainsShort(double.tryParse(_stGainsCtrl.text) ?? 0);
      notifier.setCapitalGainsLong(double.tryParse(_ltGainsCtrl.text) ?? 0);
    }

    // Deductions
    notifier.setMortgageInterest(double.tryParse(_mortgageCtrl.text) ?? 0);
    notifier.setSaltPaid(double.tryParse(_saltCtrl.text) ?? 0);
    notifier.setCharitableContributions(
        double.tryParse(_charitableCtrl.text) ?? 0);
    notifier.setMedicalExpenses(double.tryParse(_medicalCtrl.text) ?? 0);

    // Retirement
    notifier.setContributions401k(double.tryParse(_ctrl401k.text) ?? 0);
    notifier.setIraContributions(double.tryParse(_iraCtrl.text) ?? 0);
    notifier.setHsaContributions(double.tryParse(_hsaCtrl.text) ?? 0);
    notifier.setStudentLoanInterest(
        double.tryParse(_studentLoanCtrl.text) ?? 0);

    // Family
    notifier.setNumChildrenUnder17(int.tryParse(_childrenCtrl.text) ?? 0);
    notifier.setNumOtherDependents(
        int.tryParse(_otherDependentsCtrl.text) ?? 0);
    notifier.setEducationExpenses(
        double.tryParse(_educationExpCtrl.text) ?? 0);
    notifier.setEducationType(_educationType);
    notifier.setAgeOver50(_ageOver50);

    ref.read(taxResultProvider.notifier).calculate();
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider);
    final isLoading = ref.watch(taxResultProvider).isLoading;

    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Your Income',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  )),
          const SizedBox(height: 4),
          Text(
            'Enter what you know — you can always come back and update.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 20),

          // Filing status & state
          _SectionHeader(title: 'Basic info'),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'Filing status',
              helperText: 'Not sure? Single if unmarried, Joint if married.',
              border: OutlineInputBorder(),
            ),
            value: settings.filingStatus,
            items: const [
              DropdownMenuItem(value: 'single', child: Text('Single')),
              DropdownMenuItem(
                  value: 'married_jointly',
                  child: Text('Married Filing Jointly')),
              DropdownMenuItem(
                  value: 'married_separately',
                  child: Text('Married Filing Separately')),
              DropdownMenuItem(
                  value: 'head_of_household',
                  child: Text('Head of Household')),
            ],
            onChanged: (v) =>
                ref.read(settingsProvider.notifier).setFilingStatus(v!),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'State',
              border: OutlineInputBorder(),
            ),
            value: settings.state,
            items: const [
              DropdownMenuItem(
                  value: 'WA', child: Text('Washington — no income tax')),
              DropdownMenuItem(value: 'CA', child: Text('California')),
              DropdownMenuItem(value: 'NY', child: Text('New York')),
              DropdownMenuItem(
                  value: 'TX', child: Text('Texas — no income tax')),
              DropdownMenuItem(
                  value: 'FL', child: Text('Florida — no income tax')),
            ],
            onChanged: (v) =>
                ref.read(settingsProvider.notifier).setState(v!),
          ),

          const SizedBox(height: 24),

          // === Basic income fields ===
          _SectionHeader(title: 'Income'),
          const SizedBox(height: 8),
          _CurrencyField(
            controller: _wagesCtrl,
            label: 'Salary / wages',
            helper:
                'Your annual pay before taxes (from your W-2 or offer letter)',
          ),
          const SizedBox(height: 12),
          _CurrencyField(
            controller: _fedWithheldCtrl,
            label: 'Tax already withheld (federal)',
            helper:
                'Check your latest pay stub — look for "Federal Tax Withheld YTD"',
          ),
          const SizedBox(height: 12),
          _CurrencyField(
            controller: _stateWithheldCtrl,
            label: 'Tax already withheld (state)',
            helper: 'On your pay stub — "State Tax Withheld YTD"',
          ),

          const SizedBox(height: 16),

          // === Additional income toggle ===
          _CollapsibleToggle(
            expanded: _showDetailed,
            collapsedLabel:
                'I have stock income, investments, or other income',
            expandedLabel: 'Hide additional income',
            onTap: () => setState(() => _showDetailed = !_showDetailed),
          ),

          if (_showDetailed) ...[
            const SizedBox(height: 12),
            _CurrencyFieldWithGlossary(
              controller: _rsuCtrl,
              label: 'Stock awards (RSU)',
              glossaryKey: 'rsu_income',
              helper: 'Value of company stock that vested this year',
            ),
            const SizedBox(height: 12),
            _CurrencyFieldWithGlossary(
              controller: _stGainsCtrl,
              label: 'Short-term investment gains',
              glossaryKey: 'capital_gains_short',
              helper: 'Profits from investments held less than 1 year',
            ),
            const SizedBox(height: 12),
            _CurrencyFieldWithGlossary(
              controller: _ltGainsCtrl,
              label: 'Long-term investment gains',
              glossaryKey: 'capital_gains_long',
              helper:
                  'Profits from investments held 1+ years (taxed at lower rate)',
            ),
          ],

          const SizedBox(height: 16),

          // === Deductions toggle ===
          _CollapsibleToggle(
            expanded: _showDeductions,
            collapsedLabel: 'I have deductions (mortgage, charity, etc.)',
            expandedLabel: 'Hide deductions',
            onTap: () => setState(() => _showDeductions = !_showDeductions),
          ),

          if (_showDeductions) ...[
            const SizedBox(height: 12),
            _SectionHeader(title: 'Deductions'),
            const SizedBox(height: 8),
            _CurrencyField(
              controller: _mortgageCtrl,
              label: 'Mortgage interest paid',
              helper: 'From your Form 1098',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _saltCtrl,
              label: 'State & local taxes paid (SALT)',
              helper: 'Capped at \$10,000 by law',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _charitableCtrl,
              label: 'Charitable donations',
              helper: 'Cash and non-cash donations to qualified organizations',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _medicalCtrl,
              label: 'Medical expenses',
              helper:
                  'Only the portion exceeding 7.5% of your AGI is deductible',
            ),
          ],

          const SizedBox(height: 16),

          // === Retirement & Pre-tax toggle ===
          _CollapsibleToggle(
            expanded: _showRetirement,
            collapsedLabel:
                'I contribute to retirement or pre-tax accounts',
            expandedLabel: 'Hide retirement & pre-tax',
            onTap: () => setState(() => _showRetirement = !_showRetirement),
          ),

          if (_showRetirement) ...[
            const SizedBox(height: 12),
            _SectionHeader(title: 'Retirement & Pre-tax'),
            const SizedBox(height: 8),
            _CurrencyField(
              controller: _ctrl401k,
              label: '401(k) contributions',
              helper: 'Your employee contributions this year',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _iraCtrl,
              label: 'Traditional IRA contributions',
              helper: 'Deductible if you meet income limits',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _hsaCtrl,
              label: 'HSA contributions',
              helper:
                  'Health Savings Account — fully deductible above the line',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _studentLoanCtrl,
              label: 'Student loan interest paid',
              helper: 'Up to \$2,500 deductible if you meet income limits',
            ),
          ],

          const SizedBox(height: 16),

          // === Family & Education toggle ===
          _CollapsibleToggle(
            expanded: _showFamily,
            collapsedLabel:
                'I have children, dependents, or education expenses',
            expandedLabel: 'Hide family & education',
            onTap: () => setState(() => _showFamily = !_showFamily),
          ),

          if (_showFamily) ...[
            const SizedBox(height: 12),
            _SectionHeader(title: 'Family & Education'),
            const SizedBox(height: 8),
            _IntegerField(
              controller: _childrenCtrl,
              label: 'Children under 17',
              helper: 'Qualifies for the Child Tax Credit (up to \$2,000 each)',
            ),
            const SizedBox(height: 12),
            _IntegerField(
              controller: _otherDependentsCtrl,
              label: 'Other dependents',
              helper:
                  'Non-child dependents (e.g., elderly parents, college-age kids)',
            ),
            const SizedBox(height: 12),
            _CurrencyField(
              controller: _educationExpCtrl,
              label: 'Education expenses',
              helper: 'Tuition and fees for higher education',
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'Education credit type',
                helperText:
                    'AOTC: first 4 years of college. LLC: any higher ed.',
                border: OutlineInputBorder(),
              ),
              value: _educationType,
              items: const [
                DropdownMenuItem(
                    value: 'none', child: Text('No education credit')),
                DropdownMenuItem(
                    value: 'aotc',
                    child: Text('American Opportunity Credit (AOTC)')),
                DropdownMenuItem(
                    value: 'llc',
                    child: Text('Lifetime Learning Credit (LLC)')),
              ],
              onChanged: (v) => setState(() => _educationType = v!),
            ),
            const SizedBox(height: 8),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Age 50 or older'),
              subtitle: const Text(
                  'Enables catch-up contributions for 401(k) and IRA'),
              value: _ageOver50,
              activeColor: AppColors.brand,
              onChanged: (v) => setState(() => _ageOver50 = v),
            ),
          ],

          const SizedBox(height: 24),
          SizedBox(
            height: 52,
            child: FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.brand,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
              ),
              onPressed: isLoading ? null : _calculate,
              icon: isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.calculate),
              label: Text(
                isLoading ? 'Calculating...' : 'Calculate my tax',
                style: const TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

// ─── Shared toggle widget ────────────────────────────────────────────────────

class _CollapsibleToggle extends StatelessWidget {
  const _CollapsibleToggle({
    required this.expanded,
    required this.collapsedLabel,
    required this.expandedLabel,
    required this.onTap,
  });

  final bool expanded;
  final String collapsedLabel;
  final String expandedLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Icon(
              expanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
              color: AppColors.brand,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                expanded ? expandedLabel : collapsedLabel,
                style: TextStyle(
                  color: AppColors.brand,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Section header ──────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title});
  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.brand,
            ));
  }
}

// ─── Currency field ──────────────────────────────────────────────────────────

class _CurrencyField extends StatelessWidget {
  const _CurrencyField({
    required this.controller,
    required this.label,
    this.helper,
  });
  final TextEditingController controller;
  final String label;
  final String? helper;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixText: '\$ ',
        border: const OutlineInputBorder(),
        helperText: helper,
        helperMaxLines: 2,
      ),
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
    );
  }
}

// ─── Integer field (no $ prefix) ─────────────────────────────────────────────

class _IntegerField extends StatelessWidget {
  const _IntegerField({
    required this.controller,
    required this.label,
    this.helper,
  });
  final TextEditingController controller;
  final String label;
  final String? helper;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        helperText: helper,
        helperMaxLines: 2,
      ),
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
    );
  }
}

// ─── Currency field with glossary tooltip ────────────────────────────────────

class _CurrencyFieldWithGlossary extends StatelessWidget {
  const _CurrencyFieldWithGlossary({
    required this.controller,
    required this.label,
    required this.glossaryKey,
    this.helper,
  });
  final TextEditingController controller;
  final String label;
  final String glossaryKey;
  final String? helper;

  @override
  Widget build(BuildContext context) {
    final entry = TaxGlossary.entries[glossaryKey];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextFormField(
          controller: controller,
          decoration: InputDecoration(
            labelText: label,
            prefixText: '\$ ',
            border: const OutlineInputBorder(),
            helperText: helper,
            helperMaxLines: 2,
            suffixIcon: entry != null
                ? IconButton(
                    icon: const Icon(Icons.info_outline, size: 20),
                    color: AppColors.textSecondary,
                    onPressed: () => _showGlossary(context, entry),
                  )
                : null,
          ),
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
        ),
      ],
    );
  }

  void _showGlossary(BuildContext context, TaxGlossaryEntry entry) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.textSecondary.withAlpha(80),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            Text(entry.friendly,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    )),
            const SizedBox(height: 4),
            Text(entry.term,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                      fontStyle: FontStyle.italic,
                    )),
            const SizedBox(height: 12),
            Text(entry.explanation,
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(height: 1.5)),
          ],
        ),
      ),
    );
  }
}
