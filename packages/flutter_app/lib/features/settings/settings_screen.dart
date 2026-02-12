import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/api_provider.dart';
import '../../core/providers/settings_provider.dart';

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

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
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
                ref.read(settingsProvider.notifier).setUserState(v!),
          ),
          const SizedBox(height: 16),
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
                const SnackBar(content: Text('Onboarding reset. Restart app to see it.')),
              );
            },
            child: const Text('Reset Onboarding'),
          ),
        ],
      ),
    );
  }
}
