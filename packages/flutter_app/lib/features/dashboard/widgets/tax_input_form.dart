import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/settings_provider.dart';
import '../dashboard_provider.dart';

class TaxInputForm extends ConsumerStatefulWidget {
  const TaxInputForm({super.key});

  @override
  ConsumerState<TaxInputForm> createState() => _TaxInputFormState();
}

class _TaxInputFormState extends ConsumerState<TaxInputForm> {
  final _formKey = GlobalKey<FormState>();
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
    _wagesCtrl = TextEditingController(text: s.wages > 0 ? s.wages.toStringAsFixed(0) : '');
    _rsuCtrl = TextEditingController(text: s.rsuIncome > 0 ? s.rsuIncome.toStringAsFixed(0) : '');
    _stGainsCtrl = TextEditingController(text: s.capitalGainsShort > 0 ? s.capitalGainsShort.toStringAsFixed(0) : '');
    _ltGainsCtrl = TextEditingController(text: s.capitalGainsLong > 0 ? s.capitalGainsLong.toStringAsFixed(0) : '');
    _fedWithheldCtrl = TextEditingController(text: s.federalWithheld > 0 ? s.federalWithheld.toStringAsFixed(0) : '');
    _stateWithheldCtrl = TextEditingController(text: s.stateWithheld > 0 ? s.stateWithheld.toStringAsFixed(0) : '');
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
    notifier.setRsuIncome(double.tryParse(_rsuCtrl.text) ?? 0);
    notifier.setCapitalGainsShort(double.tryParse(_stGainsCtrl.text) ?? 0);
    notifier.setCapitalGainsLong(double.tryParse(_ltGainsCtrl.text) ?? 0);
    notifier.setFederalWithheld(double.tryParse(_fedWithheldCtrl.text) ?? 0);
    notifier.setStateWithheld(double.tryParse(_stateWithheldCtrl.text) ?? 0);

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
          Text('Tax Input', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'Filing Status',
              border: OutlineInputBorder(),
            ),
            value: settings.filingStatus,
            items: const [
              DropdownMenuItem(value: 'single', child: Text('Single')),
              DropdownMenuItem(value: 'married_jointly', child: Text('Married Filing Jointly')),
              DropdownMenuItem(value: 'married_separately', child: Text('Married Filing Separately')),
              DropdownMenuItem(value: 'head_of_household', child: Text('Head of Household')),
            ],
            onChanged: (v) => ref.read(settingsProvider.notifier).setFilingStatus(v!),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'State',
              border: OutlineInputBorder(),
            ),
            value: settings.state,
            items: const [
              DropdownMenuItem(value: 'CA', child: Text('California')),
              DropdownMenuItem(value: 'NY', child: Text('New York')),
              DropdownMenuItem(value: 'WA', child: Text('Washington')),
            ],
            onChanged: (v) => ref.read(settingsProvider.notifier).setState(v!),
          ),
          const SizedBox(height: 12),
          _CurrencyField(controller: _wagesCtrl, label: 'W-2 Wages'),
          const SizedBox(height: 12),
          _CurrencyField(controller: _rsuCtrl, label: 'RSU Income'),
          const SizedBox(height: 12),
          _CurrencyField(controller: _stGainsCtrl, label: 'Short-Term Capital Gains'),
          const SizedBox(height: 12),
          _CurrencyField(controller: _ltGainsCtrl, label: 'Long-Term Capital Gains'),
          const SizedBox(height: 12),
          _CurrencyField(controller: _fedWithheldCtrl, label: 'Federal Withheld YTD'),
          const SizedBox(height: 12),
          _CurrencyField(controller: _stateWithheldCtrl, label: 'State Withheld YTD'),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: isLoading ? null : _calculate,
            icon: isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.calculate),
            label: Text(isLoading ? 'Calculating...' : 'Calculate'),
          ),
        ],
      ),
    );
  }
}

class _CurrencyField extends StatelessWidget {
  const _CurrencyField({required this.controller, required this.label});
  final TextEditingController controller;
  final String label;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixText: '\$ ',
        border: const OutlineInputBorder(),
      ),
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
    );
  }
}
