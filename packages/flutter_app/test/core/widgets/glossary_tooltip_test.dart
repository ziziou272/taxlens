import 'package:flutter_test/flutter_test.dart';
import 'package:taxlens_app/core/widgets/glossary_tooltip.dart';

void main() {
  group('TaxGlossary', () {
    test('contains all expected entries', () {
      final expected = [
        'effective_rate',
        'marginal_rate',
        'w2_wages',
        'rsu_income',
        'capital_gains_short',
        'capital_gains_long',
        'withholding',
        'filing_status',
        'agi',
        'standard_deduction',
        'amt',
        'niit',
        'fica',
        'iso',
      ];

      for (final key in expected) {
        expect(TaxGlossary.entries.containsKey(key), isTrue,
            reason: 'Missing glossary entry: $key');
      }
    });

    test('all entries have non-empty fields', () {
      for (final entry in TaxGlossary.entries.entries) {
        expect(entry.value.term.isNotEmpty, isTrue,
            reason: '${entry.key} has empty term');
        expect(entry.value.friendly.isNotEmpty, isTrue,
            reason: '${entry.key} has empty friendly name');
        expect(entry.value.explanation.isNotEmpty, isTrue,
            reason: '${entry.key} has empty explanation');
        expect(entry.value.explanation.length > 50, isTrue,
            reason: '${entry.key} explanation too short (${entry.value.explanation.length} chars)');
      }
    });

    test('has exactly 14 entries', () {
      expect(TaxGlossary.entries.length, 14);
    });

    test('friendly names differ from technical terms', () {
      for (final entry in TaxGlossary.entries.entries) {
        expect(entry.value.friendly != entry.value.term, isTrue,
            reason: '${entry.key}: friendly should differ from term');
      }
    });
  });
}
