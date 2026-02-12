import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/providers/api_provider.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/providers/settings_provider.dart';
import '../../core/theme/app_colors.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  late final TextEditingController _apiUrlController;

  @override
  void initState() {
    super.initState();
    _apiUrlController =
        TextEditingController(text: ref.read(apiBaseUrlProvider));
  }

  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider);
    final isAuthenticated = ref.watch(isAuthenticatedProvider);
    final user = ref.watch(currentUserProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Account section
          if (isAuthenticated) ...[
            Card(
              child: ListTile(
                leading: const Icon(Icons.person, color: AppColors.brand),
                title: Text(user?.email ?? 'Account'),
                subtitle: const Text('View profile & account settings'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go('/profile'),
              ),
            ),
            const SizedBox(height: 16),
          ] else ...[
            Card(
              child: ListTile(
                leading: const Icon(Icons.login, color: AppColors.brand),
                title: const Text('Sign In'),
                subtitle: const Text('Save your data across devices'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go('/login'),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Tax settings
          Text('Tax Profile', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'Filing Status',
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
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'State',
              border: OutlineInputBorder(),
            ),
            value: settings.state,
            items: const [
              DropdownMenuItem(value: 'CA', child: Text('California')),
              DropdownMenuItem(value: 'NY', child: Text('New York')),
              DropdownMenuItem(value: 'TX', child: Text('Texas')),
              DropdownMenuItem(value: 'WA', child: Text('Washington')),
              DropdownMenuItem(value: 'FL', child: Text('Florida')),
            ],
            onChanged: (v) =>
                ref.read(settingsProvider.notifier).setState(v!),
          ),
          const SizedBox(height: 24),

          // API settings
          Text('Advanced', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          TextFormField(
            controller: _apiUrlController,
            decoration: const InputDecoration(
              labelText: 'API Base URL',
              border: OutlineInputBorder(),
              helperText: 'e.g. http://localhost:8100',
            ),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: () {
              ref.read(apiBaseUrlProvider.notifier).state =
                  _apiUrlController.text.trim();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Settings saved')),
              );
            },
            child: const Text('Save Settings'),
          ),
          const SizedBox(height: 16),
          OutlinedButton(
            onPressed: () {
              ref.read(settingsProvider.notifier).setOnboardingComplete(false);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                    content:
                        Text('Onboarding reset. Restart app to see it.')),
              );
            },
            child: const Text('Reset Onboarding'),
          ),

          if (isAuthenticated) ...[
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: () async {
                await ref.read(authServiceProvider).signOut();
                if (context.mounted) context.go('/');
              },
              icon: const Icon(Icons.logout),
              label: const Text('Sign Out'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.negative,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
