import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import 'tax_returns_provider.dart';
import 'tax_return_model.dart';

class ReviewExtractionScreen extends ConsumerStatefulWidget {
  const ReviewExtractionScreen({super.key, required this.extraction});
  final TaxReturnExtraction extraction;

  @override
  ConsumerState<ReviewExtractionScreen> createState() =>
      _ReviewExtractionScreenState();
}

class _ReviewExtractionScreenState
    extends ConsumerState<ReviewExtractionScreen> {
  late Map<String, TextEditingController> _controllers;
  bool _saving = false;

  static const _fieldMeta = <String, _FieldMeta>{
    'tax_year': _FieldMeta('Tax Year', Icons.calendar_today, isYear: true),
    'filing_status': _FieldMeta('Filing Status', Icons.people, isText: true),
    'total_income': _FieldMeta('Total Income', Icons.attach_money),
    'adjusted_gross_income':
        _FieldMeta('Adjusted Gross Income (AGI)', Icons.account_balance),
    'deduction_type':
        _FieldMeta('Deduction Type', Icons.deblur, isText: true),
    'deduction_amount': _FieldMeta('Deduction Amount', Icons.remove_circle_outline),
    'taxable_income': _FieldMeta('Taxable Income', Icons.calculate),
    'total_tax': _FieldMeta('Total Tax', Icons.receipt),
    'total_credits': _FieldMeta('Total Credits', Icons.card_giftcard),
    'federal_withheld': _FieldMeta('Federal Tax Withheld', Icons.account_balance_wallet),
    'refund_or_owed': _FieldMeta('Refund (+) / Owed (-)', Icons.swap_vert),
  };

  @override
  void initState() {
    super.initState();
    final fields = widget.extraction.toEditableFields();
    _controllers = {
      for (final entry in fields.entries)
        entry.key: TextEditingController(text: entry.value),
    };
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  Map<String, String> get _currentFields =>
      _controllers.map((k, c) => MapEntry(k, c.text.trim()));

  Future<void> _confirm() async {
    setState(() => _saving = true);
    try {
      final data = widget.extraction.toConfirmJson(_currentFields);
      await ref.read(taxReturnsProvider.notifier).confirmExtraction(data);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Tax return saved!'),
            backgroundColor: AppColors.positive,
          ),
        );
        // Navigate back to the list
        context.go('/tax-returns');
      }
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save: $e'),
            backgroundColor: AppColors.negative,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final confidence = widget.extraction.extractionConfidence ?? 0.8;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Review Extraction'),
        actions: [
          if (!_saving)
            TextButton.icon(
              onPressed: _confirm,
              icon: const Icon(Icons.check),
              label: const Text('Confirm'),
            ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Confidence banner
          _ConfidenceBanner(confidence: confidence),
          const SizedBox(height: 20),

          Text(
            'Review and edit any values below before saving.',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
          ),
          const SizedBox(height: 16),

          // Fields
          ...(_fieldMeta.entries.map((entry) {
            final key = entry.key;
            final meta = entry.value;
            final ctrl = _controllers[key];
            if (ctrl == null) return const SizedBox.shrink();
            final fieldConf = widget.extraction.confidenceFor(key);
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _ExtractionField(
                meta: meta,
                controller: ctrl,
                confidence: fieldConf,
              ),
            );
          })).toList(),

          const SizedBox(height: 24),

          // Confirm button
          if (_saving)
            const Center(child: CircularProgressIndicator())
          else
            FilledButton.icon(
              onPressed: _confirm,
              icon: const Icon(Icons.save),
              label: const Text('Save Tax Return'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.all(16),
              ),
            ),
          const SizedBox(height: 8),
          Center(
            child: Text(
              'You can always edit or delete this later.',
              style: TextStyle(
                  color: AppColors.textSecondary, fontSize: 12),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

class _ConfidenceBanner extends StatelessWidget {
  const _ConfidenceBanner({required this.confidence});
  final double confidence;

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).round();
    Color bannerColor;
    String message;
    IconData icon;

    if (confidence >= 0.85) {
      bannerColor = AppColors.positive;
      message = 'High confidence extraction ($pct%) — looks good!';
      icon = Icons.check_circle_outline;
    } else if (confidence >= 0.65) {
      bannerColor = AppColors.warning;
      message = 'Medium confidence ($pct%) — please review highlighted fields';
      icon = Icons.warning_amber_outlined;
    } else {
      bannerColor = AppColors.negative;
      message = 'Low confidence ($pct%) — please carefully verify all fields';
      icon = Icons.error_outline;
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: bannerColor.withAlpha(30),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: bannerColor.withAlpha(80)),
      ),
      child: Row(
        children: [
          Icon(icon, color: bannerColor, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI Extraction Complete',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    color: bannerColor,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  message,
                  style: TextStyle(fontSize: 12, color: bannerColor),
                ),
              ],
            ),
          ),
          // Confidence ring
          SizedBox(
            width: 40,
            height: 40,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: confidence,
                  backgroundColor: bannerColor.withAlpha(40),
                  color: bannerColor,
                  strokeWidth: 4,
                ),
                Text(
                  '$pct',
                  style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: bannerColor),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ExtractionField extends StatelessWidget {
  const _ExtractionField({
    required this.meta,
    required this.controller,
    required this.confidence,
  });

  final _FieldMeta meta;
  final TextEditingController controller;
  final double confidence;

  @override
  Widget build(BuildContext context) {
    final isLowConf = confidence < 0.7;
    final borderColor = isLowConf ? AppColors.warning : AppColors.brand;

    final inputDecoration = InputDecoration(
      labelText: meta.label,
      prefixIcon: Icon(meta.icon, size: 20),
      suffixIcon: isLowConf
          ? Tooltip(
              message: 'Low confidence — please verify',
              child: Icon(Icons.warning_amber, color: AppColors.warning, size: 18),
            )
          : Icon(Icons.check_circle, color: AppColors.positive.withAlpha(180), size: 18),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: borderColor.withAlpha(isLowConf ? 160 : 60)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: AppColors.brand, width: 2),
      ),
      filled: isLowConf,
      fillColor: isLowConf ? AppColors.warning.withAlpha(15) : null,
    );

    return TextField(
      controller: controller,
      decoration: inputDecoration,
      keyboardType: (meta.isText || meta.isYear)
          ? TextInputType.text
          : const TextInputType.numberWithOptions(decimal: true, signed: true),
      inputFormatters: (meta.isText || meta.isYear)
          ? []
          : [
              FilteringTextInputFormatter.allow(RegExp(r'[-0-9.,]')),
            ],
    );
  }
}

class _FieldMeta {
  const _FieldMeta(this.label, this.icon,
      {this.isText = false, this.isYear = false});
  final String label;
  final IconData icon;
  final bool isText;
  final bool isYear;
}
