import 'package:flutter/material.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  String _filingStatus = 'single';
  String _state = 'CA';
  final _apiUrlController =
      TextEditingController(text: 'http://localhost:8100');

  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
            value: _filingStatus,
            items: const [
              DropdownMenuItem(value: 'single', child: Text('Single')),
              DropdownMenuItem(
                  value: 'married_joint',
                  child: Text('Married Filing Jointly')),
              DropdownMenuItem(
                  value: 'married_separate',
                  child: Text('Married Filing Separately')),
              DropdownMenuItem(
                  value: 'head_of_household',
                  child: Text('Head of Household')),
            ],
            onChanged: (v) => setState(() => _filingStatus = v!),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: 'State',
              border: OutlineInputBorder(),
            ),
            value: _state,
            items: const [
              DropdownMenuItem(value: 'CA', child: Text('California')),
              DropdownMenuItem(value: 'NY', child: Text('New York')),
              DropdownMenuItem(value: 'TX', child: Text('Texas')),
              DropdownMenuItem(value: 'WA', child: Text('Washington')),
              DropdownMenuItem(value: 'FL', child: Text('Florida')),
            ],
            onChanged: (v) => setState(() => _state = v!),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _apiUrlController,
            decoration: const InputDecoration(
              labelText: 'API Base URL',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Settings saved (mock)')),
              );
            },
            child: const Text('Save Settings'),
          ),
        ],
      ),
    );
  }
}
