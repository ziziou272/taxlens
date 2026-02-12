import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/providers/settings_provider.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _controller = PageController();
  int _page = 0;

  String _filingStatus = 'single';
  String _state = 'CA';
  String _incomeRange = '100k-250k';

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _next() {
    if (_page < 2) {
      _controller.nextPage(
          duration: const Duration(milliseconds: 300), curve: Curves.ease);
    } else {
      _finish();
    }
  }

  void _finish() {
    final notifier = ref.read(settingsProvider.notifier);
    notifier.setFilingStatus(_filingStatus);
    notifier.setState(_state);

    // Set approximate wages from income range
    final wages = switch (_incomeRange) {
      '0-50k' => 35000.0,
      '50k-100k' => 75000.0,
      '100k-250k' => 175000.0,
      '250k-500k' => 375000.0,
      '500k+' => 600000.0,
      _ => 100000.0,
    };
    notifier.setWages(wages);
    notifier.setOnboardingComplete(true);
    context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: PageView(
                controller: _controller,
                onPageChanged: (p) => setState(() => _page = p),
                children: [
                  _StepPage(
                    title: 'Filing Status',
                    subtitle: 'How do you file your taxes?',
                    child: _buildFilingStatus(),
                  ),
                  _StepPage(
                    title: 'State of Residence',
                    subtitle: 'Where do you live?',
                    child: _buildStateSelect(),
                  ),
                  _StepPage(
                    title: 'Income Range',
                    subtitle: 'Approximate annual income',
                    child: _buildIncomeRange(),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                children: [
                  // Dots
                  ...List.generate(3, (i) => Container(
                    width: 8, height: 8,
                    margin: const EdgeInsets.only(right: 8),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: i == _page
                          ? Theme.of(context).colorScheme.primary
                          : Theme.of(context).colorScheme.outline,
                    ),
                  )),
                  const Spacer(),
                  FilledButton(
                    onPressed: _next,
                    child: Text(_page == 2 ? 'Get Started' : 'Next'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilingStatus() {
    return Column(
      children: [
        for (final entry in {
          'single': 'Single',
          'married_jointly': 'Married Filing Jointly',
          'married_separately': 'Married Filing Separately',
          'head_of_household': 'Head of Household',
        }.entries)
          RadioListTile<String>(
            title: Text(entry.value),
            value: entry.key,
            groupValue: _filingStatus,
            onChanged: (v) => setState(() => _filingStatus = v!),
          ),
      ],
    );
  }

  Widget _buildStateSelect() {
    return Column(
      children: [
        for (final entry in {
          'CA': 'California',
          'NY': 'New York',
          'WA': 'Washington',
          'TX': 'Texas',
          'FL': 'Florida',
        }.entries)
          RadioListTile<String>(
            title: Text(entry.value),
            value: entry.key,
            groupValue: _state,
            onChanged: (v) => setState(() => _state = v!),
          ),
      ],
    );
  }

  Widget _buildIncomeRange() {
    return Column(
      children: [
        for (final entry in {
          '0-50k': 'Under \$50,000',
          '50k-100k': '\$50,000 - \$100,000',
          '100k-250k': '\$100,000 - \$250,000',
          '250k-500k': '\$250,000 - \$500,000',
          '500k+': '\$500,000+',
        }.entries)
          RadioListTile<String>(
            title: Text(entry.value),
            value: entry.key,
            groupValue: _incomeRange,
            onChanged: (v) => setState(() => _incomeRange = v!),
          ),
      ],
    );
  }
}

class _StepPage extends StatelessWidget {
  const _StepPage({
    required this.title,
    required this.subtitle,
    required this.child,
  });
  final String title;
  final String subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 48),
          Text(title, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(subtitle, style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 32),
          child,
        ],
      ),
    );
  }
}
