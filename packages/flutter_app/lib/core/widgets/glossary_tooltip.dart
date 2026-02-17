import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// A tax term with an inline ℹ️ tooltip that explains it in plain language.
///
/// Usage:
/// ```dart
/// GlossaryTerm(
///   term: 'AGI',
///   friendly: 'Adjusted Gross Income',
///   explanation: 'Your total income minus certain deductions...',
/// )
/// ```
class GlossaryTerm extends StatelessWidget {
  const GlossaryTerm({
    super.key,
    required this.term,
    this.friendly,
    required this.explanation,
    this.style,
    this.iconSize = 14,
  });

  /// The technical term displayed.
  final String term;

  /// Optional friendly name shown instead of [term].
  final String? friendly;

  /// Plain-language explanation shown in the tooltip popup.
  final String explanation;

  /// Text style for the term.
  final TextStyle? style;

  /// Size of the info icon.
  final double iconSize;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => _showExplanation(context),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(friendly ?? term, style: style),
          const SizedBox(width: 4),
          Icon(Icons.info_outline,
              size: iconSize, color: AppColors.textSecondary),
        ],
      ),
    );
  }

  void _showExplanation(BuildContext context) {
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
            // Handle bar
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
            if (friendly != null && friendly != term) ...[
              Text(friendly!,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      )),
              const SizedBox(height: 4),
              Text(term,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                        fontStyle: FontStyle.italic,
                      )),
            ] else
              Text(term,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      )),
            const SizedBox(height: 12),
            Text(explanation,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      height: 1.5,
                    )),
          ],
        ),
      ),
    );
  }
}

/// Static glossary data for all tax terms used in the app.
class TaxGlossary {
  TaxGlossary._();

  static const entries = <String, TaxGlossaryEntry>{
    'effective_rate': TaxGlossaryEntry(
      term: 'Effective Tax Rate',
      friendly: 'Average tax rate',
      explanation:
          'Your total tax divided by your total income. It tells you what percentage of your income actually goes to taxes. For example, if you earn \$100,000 and pay \$23,000 in tax, your effective rate is 23%.',
    ),
    'marginal_rate': TaxGlossaryEntry(
      term: 'Marginal Tax Rate',
      friendly: 'Top tax rate',
      explanation:
          'The tax rate on your next dollar of income. The US uses "brackets" — your first dollars are taxed at low rates, and each chunk of income above that is taxed at a higher rate. Your marginal rate is only the rate on the top chunk, not on everything you earn.',
    ),
    'w2_wages': TaxGlossaryEntry(
      term: 'W-2 Wages',
      friendly: 'Salary / paycheck income',
      explanation:
          'The income from your job. Your employer reports this on a W-2 form. It includes your salary, bonuses, and tips before any deductions.',
    ),
    'rsu_income': TaxGlossaryEntry(
      term: 'RSU Income',
      friendly: 'Stock award income',
      explanation:
          'Restricted Stock Units — shares your company gives you as compensation. When they "vest" (become yours), their value counts as taxable income, just like a paycheck.',
    ),
    'capital_gains_short': TaxGlossaryEntry(
      term: 'Short-Term Capital Gains',
      friendly: 'Quick investment profits',
      explanation:
          'Profit from selling investments you held for less than 1 year. These are taxed at your regular income tax rate (the same as your paycheck).',
    ),
    'capital_gains_long': TaxGlossaryEntry(
      term: 'Long-Term Capital Gains',
      friendly: 'Investment profits (1+ year)',
      explanation:
          'Profit from selling investments you held for more than 1 year. These get a lower tax rate (0%, 15%, or 20%) — one of the best tax advantages available.',
    ),
    'withholding': TaxGlossaryEntry(
      term: 'Tax Withholding',
      friendly: 'Tax already paid from paychecks',
      explanation:
          'The tax your employer takes out of each paycheck and sends to the IRS on your behalf. At tax time, if they withheld too much, you get a refund. Too little, and you owe.',
    ),
    'filing_status': TaxGlossaryEntry(
      term: 'Filing Status',
      friendly: 'How you file',
      explanation:
          'Your tax filing category. It affects your tax brackets, standard deduction, and eligibility for credits. Most people are either "Single" or "Married Filing Jointly."',
    ),
    'agi': TaxGlossaryEntry(
      term: 'AGI (Adjusted Gross Income)',
      friendly: 'Your income after adjustments',
      explanation:
          'Your total income minus specific deductions (like 401(k) contributions, student loan interest, etc.). Many tax benefits have AGI thresholds — if your AGI is too high, you may not qualify.',
    ),
    'standard_deduction': TaxGlossaryEntry(
      term: 'Standard Deduction',
      friendly: 'Free tax-exempt amount',
      explanation:
          'An amount of income the government automatically exempts from tax. For 2026, it\'s about \$15,000 for single filers and \$30,000 for married couples. You don\'t need receipts — everyone gets it unless they choose to itemize.',
    ),
    'amt': TaxGlossaryEntry(
      term: 'AMT (Alternative Minimum Tax)',
      friendly: 'Alternative minimum tax',
      explanation:
          'A parallel tax system designed to ensure high earners pay at least a minimum amount. It can kick in if you have large stock option exercises, lots of deductions, or high income. Most people don\'t owe AMT.',
    ),
    'niit': TaxGlossaryEntry(
      term: 'NIIT (Net Investment Income Tax)',
      friendly: 'Investment surtax',
      explanation:
          'An extra 3.8% tax on investment income (dividends, capital gains, rental income) for individuals earning above \$200,000 (single) or \$250,000 (married). It was introduced to fund healthcare.',
    ),
    'fica': TaxGlossaryEntry(
      term: 'FICA',
      friendly: 'Social Security & Medicare tax',
      explanation:
          'Federal Insurance Contributions Act tax — the 7.65% taken from your paycheck for Social Security (6.2%) and Medicare (1.45%). Your employer pays a matching 7.65%. Self-employed people pay both halves (15.3%).',
    ),
    'iso': TaxGlossaryEntry(
      term: 'ISO (Incentive Stock Options)',
      friendly: 'Employee stock options',
      explanation:
          'A type of stock option with special tax treatment. You don\'t owe regular income tax when you exercise them, but you may owe AMT. If you hold the shares long enough, profits are taxed as long-term capital gains instead of income.',
    ),
  };
}

class TaxGlossaryEntry {
  final String term;
  final String friendly;
  final String explanation;

  const TaxGlossaryEntry({
    required this.term,
    required this.friendly,
    required this.explanation,
  });
}
