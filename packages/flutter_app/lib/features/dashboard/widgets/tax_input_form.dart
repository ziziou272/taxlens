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

  late final TextEditingController _wagesCtrl;
  late final TextEditingController _rsuCtrl;
  late final TextEditingController _stGainsCtrl;
  late final TextEditingController _ltGainsCtrl;
  late final TextEditingController _fedWithheldCtrl;
  late final TextEditingController _stateWithheldCtrl;

  @override
  void initState() {
    super.initState();
    final s = ref.read(settingsProvider);
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

    // Auto-show detailed if user already has advanced fields filled
    if (s.rsuIncome > 0 ||
        s.capitalGainsShort > 0 ||
        s.capitalGainsLong > 0) {
      _showDetailed = true;
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
    super.dispose();
  }

  void _calculate() {
    if (!_formKey.currentState!.validate()) return;

    final notifier = ref.read(settingsProvider.notifier);
    notifier.setWages(double.tryParse(_wagesCtrl.text) ?? 0);
    notifier.setFederalWithheld(double.tryParse(_fedWithheldCtrl.text) ?? 0);
    notifier.setStateWithheld(double.tryParse(_stateWithheldCtrl.text) ?? 0);

    if (_showDetailed) {
      notifier.setRsuIncome(double.tryParse(_rsuCtrl.text) ?? 0);
      notifier
          .setCapitalGainsShort(double.tryParse(_stGainsCtrl.text) ?? 0);
      notifier.setCapitalGainsLong(double.tryParse(_ltGainsCtrl.text) ?? 0);
    }

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
              DropdownMenuItem(value: 'WA', child: Text('Washington — no income tax')),
              DropdownMenuItem(value: 'CA', child: Text('California')),
              DropdownMenuItem(value: 'NY', child: Text('New York')),
              DropdownMenuItem(value: 'TX', child: Text('Texas — no income tax')),
              DropdownMenuItem(value: 'FL', child: Text('Florida — no income tax')),
            ],
            onChanged: (v) =>
                ref.read(settingsProvider.notifier).setState(v!),
          ),

          const SizedBox(height: 24),

          // === Basic fields ===
          _SectionHeader(title: 'Income'),
          const SizedBox(height: 8),
          _CurrencyField(
            controller: _wagesCtrl,
            label: 'Salary / wages',
            helper: 'Your annual pay before taxes (from your W-2 or offer letter)',
          ),
          const SizedBox(height: 12),
          _CurrencyField(
            controller: _fedWithheldCtrl,
            label: 'Tax already withheld (federal)',
            helper: 'Check your latest pay stub — look for "Federal Tax Withheld YTD"',
          ),
          const SizedBox(height: 12),
          _CurrencyField(
            controller: _stateWithheldCtrl,
            label: 'Tax already withheld (state)',
            helper: 'On your pay stub — "State Tax Withheld YTD"',
          ),

          const SizedBox(height: 16),

          // === Detailed toggle ===
          InkWell(
            onTap: () => setState(() => _showDetailed = !_showDetailed),
            borderRadius: BorderRadius.circular(8),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Row(
                children: [
                  Icon(
                    _showDetailed
                        ? Icons.keyboard_arrow_up
                        : Icons.keyboard_arrow_down,
                    color: AppColors.brand,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _showDetailed
                        ? 'Hide additional income'
                        : 'I have stock income, investments, or other income',
                    style: TextStyle(
                      color: AppColors.brand,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // === Detailed fields ===
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
              helper: 'Profits from investments held 1+ years (taxed at lower rate)',
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
                      child:
                          CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
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
