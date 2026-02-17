import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/providers/settings_provider.dart';
import '../../core/theme/app_colors.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _controller = PageController();
  int _page = 0;
  static const _totalPages = 5;

  String _filingStatus = 'single';
  String _state = 'WA';
  String _incomeRange = '100k-250k';

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _next() {
    if (_page < _totalPages - 1) {
      _controller.nextPage(
          duration: const Duration(milliseconds: 300), curve: Curves.ease);
    } else {
      _finish();
    }
  }

  void _back() {
    if (_page > 0) {
      _controller.previousPage(
          duration: const Duration(milliseconds: 300), curve: Curves.ease);
    }
  }

  void _finish() {
    final notifier = ref.read(settingsProvider.notifier);
    notifier.setFilingStatus(_filingStatus);
    notifier.setState(_state);

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
                  // Page 1: Value Proposition
                  _ValuePage(
                    icon: Icons.savings_outlined,
                    iconSize: 80,
                    title: 'See your taxes clearly',
                    subtitle: 'Know exactly what you owe — and how to pay less.',
                    features: const [
                      _FeatureItem(
                        icon: Icons.calculate_outlined,
                        text: 'Calculate your total tax in seconds',
                      ),
                      _FeatureItem(
                        icon: Icons.lightbulb_outline,
                        text: 'Get personalized tips to save money',
                      ),
                      _FeatureItem(
                        icon: Icons.compare_arrows,
                        text: 'See how life changes affect your taxes',
                      ),
                    ],
                  ),
                  // Page 2: How It Works
                  _ValuePage(
                    icon: Icons.rocket_launch_outlined,
                    iconSize: 64,
                    title: 'Three steps to savings',
                    subtitle: 'Simple enough. No accounting degree needed.',
                    features: const [
                      _FeatureItem(
                        icon: Icons.edit_outlined,
                        number: '1',
                        text: 'Enter your income — we calculate your tax',
                      ),
                      _FeatureItem(
                        icon: Icons.notifications_outlined,
                        number: '2',
                        text: 'Get alerts when there\'s a chance to save',
                      ),
                      _FeatureItem(
                        icon: Icons.explore_outlined,
                        number: '3',
                        text: 'Try "What if..." to explore tax scenarios',
                      ),
                    ],
                  ),
                  // Page 3: Filing Status
                  _StepPage(
                    title: 'How do you file?',
                    subtitle:
                        'This determines your tax brackets. Not sure? Most single people choose "Single" and married couples choose "Married Filing Jointly."',
                    child: _buildFilingStatus(),
                  ),
                  // Page 4: State
                  _StepPage(
                    title: 'Where do you live?',
                    subtitle:
                        'Each state has different tax rates. Some states (like Washington and Texas) have no income tax!',
                    child: _buildStateSelect(),
                  ),
                  // Page 5: Income Range
                  _StepPage(
                    title: 'Roughly how much do you earn?',
                    subtitle:
                        'Just a ballpark — you can enter exact numbers later. This is your total annual income before taxes.',
                    child: _buildIncomeRange(),
                  ),
                ],
              ),
            ),
            // Navigation bar
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
              child: Row(
                children: [
                  // Back button (hidden on first page)
                  if (_page > 0)
                    TextButton(
                      onPressed: _back,
                      child: const Text('Back'),
                    )
                  else
                    const SizedBox(width: 72),
                  const Spacer(),
                  // Page dots
                  ...List.generate(_totalPages, (i) => Container(
                    width: i == _page ? 24 : 8,
                    height: 8,
                    margin: const EdgeInsets.only(right: 6),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(4),
                      color: i == _page
                          ? AppColors.brand
                          : AppColors.brand.withAlpha(60),
                    ),
                  )),
                  const Spacer(),
                  FilledButton(
                    onPressed: _next,
                    style: FilledButton.styleFrom(
                      backgroundColor: AppColors.brand,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 24, vertical: 12),
                    ),
                    child: Text(_page == _totalPages - 1
                        ? 'Get Started'
                        : _page < 2
                            ? 'Next'
                            : 'Continue'),
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
    final options = {
      'single': ('Single', 'Not married, no dependents'),
      'married_jointly': ('Married Filing Jointly', 'Married, filing together — usually the best deal'),
      'married_separately': ('Married Filing Separately', 'Married, but filing on your own'),
      'head_of_household': ('Head of Household', 'Unmarried and paying for a dependent'),
    };
    return Column(
      children: options.entries.map((e) {
        final selected = _filingStatus == e.key;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Material(
            color: selected ? AppColors.brand.withAlpha(30) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            child: ListTile(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(
                  color: selected ? AppColors.brand : Colors.white12,
                ),
              ),
              leading: Icon(
                selected ? Icons.check_circle : Icons.circle_outlined,
                color: selected ? AppColors.brand : AppColors.textSecondary,
              ),
              title: Text(e.value.$1,
                  style: TextStyle(
                    fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                  )),
              subtitle: Text(e.value.$2,
                  style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
              onTap: () => setState(() => _filingStatus = e.key),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildStateSelect() {
    final states = {
      'WA': ('Washington', 'No state income tax ✨'),
      'CA': ('California', 'Up to 13.3% state tax'),
      'NY': ('New York', 'Up to 10.9% state tax'),
      'TX': ('Texas', 'No state income tax ✨'),
      'FL': ('Florida', 'No state income tax ✨'),
    };
    return Column(
      children: states.entries.map((e) {
        final selected = _state == e.key;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Material(
            color: selected ? AppColors.brand.withAlpha(30) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            child: ListTile(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(
                  color: selected ? AppColors.brand : Colors.white12,
                ),
              ),
              leading: Icon(
                selected ? Icons.check_circle : Icons.circle_outlined,
                color: selected ? AppColors.brand : AppColors.textSecondary,
              ),
              title: Text(e.value.$1,
                  style: TextStyle(
                    fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                  )),
              subtitle: Text(e.value.$2,
                  style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
              onTap: () => setState(() => _state = e.key),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildIncomeRange() {
    final ranges = {
      '0-50k': ('Under \$50,000', '💡 You may qualify for tax credits'),
      '50k-100k': ('\$50,000 – \$100,000', ''),
      '100k-250k': ('\$100,000 – \$250,000', ''),
      '250k-500k': ('\$250,000 – \$500,000', '💡 AMT may apply to you'),
      '500k+': ('\$500,000+', '💡 Additional Medicare & investment taxes may apply'),
    };
    return Column(
      children: ranges.entries.map((e) {
        final selected = _incomeRange == e.key;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Material(
            color: selected ? AppColors.brand.withAlpha(30) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            child: ListTile(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(
                  color: selected ? AppColors.brand : Colors.white12,
                ),
              ),
              leading: Icon(
                selected ? Icons.check_circle : Icons.circle_outlined,
                color: selected ? AppColors.brand : AppColors.textSecondary,
              ),
              title: Text(e.value.$1,
                  style: TextStyle(
                    fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                  )),
              subtitle: e.value.$2.isNotEmpty
                  ? Text(e.value.$2,
                      style: const TextStyle(fontSize: 12, color: AppColors.textSecondary))
                  : null,
              onTap: () => setState(() => _incomeRange = e.key),
            ),
          ),
        );
      }).toList(),
    );
  }
}

// ─── Value / Intro Pages ───

class _FeatureItem {
  final IconData icon;
  final String text;
  final String? number;
  const _FeatureItem({required this.icon, required this.text, this.number});
}

class _ValuePage extends StatelessWidget {
  const _ValuePage({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.features,
    this.iconSize = 64,
  });
  final IconData icon;
  final double iconSize;
  final String title;
  final String subtitle;
  final List<_FeatureItem> features;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const Spacer(flex: 2),
          Container(
            width: iconSize + 40,
            height: iconSize + 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.brand.withAlpha(25),
            ),
            child: Icon(icon, size: iconSize, color: AppColors.brand),
          ),
          const SizedBox(height: 32),
          Text(title,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center),
          const SizedBox(height: 12),
          Text(subtitle,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: AppColors.textSecondary,
                  ),
              textAlign: TextAlign.center),
          const SizedBox(height: 40),
          ...features.map((f) => Padding(
                padding: const EdgeInsets.only(bottom: 20),
                child: Row(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        color: AppColors.brand.withAlpha(20),
                      ),
                      child: f.number != null
                          ? Center(
                              child: Text(f.number!,
                                  style: const TextStyle(
                                    color: AppColors.brand,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 18,
                                  )))
                          : Icon(f.icon, color: AppColors.brand, size: 22),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(f.text,
                          style: Theme.of(context).textTheme.bodyLarge),
                    ),
                  ],
                ),
              )),
          const Spacer(flex: 3),
        ],
      ),
    );
  }
}

// ─── Form Step Pages ───

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
          const SizedBox(height: 32),
          Text(title, style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          )),
          const SizedBox(height: 8),
          Text(subtitle,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  )),
          const SizedBox(height: 24),
          Expanded(child: SingleChildScrollView(child: child)),
        ],
      ),
    );
  }
}
