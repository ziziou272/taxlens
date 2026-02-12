import 'package:flutter/material.dart';

class ExtractedDataView extends StatefulWidget {
  const ExtractedDataView({
    super.key,
    required this.data,
    required this.onSave,
  });

  final Map<String, String> data;
  final void Function(Map<String, String> updated) onSave;

  @override
  State<ExtractedDataView> createState() => _ExtractedDataViewState();
}

class _ExtractedDataViewState extends State<ExtractedDataView> {
  late Map<String, TextEditingController> _controllers;

  @override
  void initState() {
    super.initState();
    _controllers = {
      for (final entry in widget.data.entries)
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

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            for (final entry in _controllers.entries) ...[
              TextFormField(
                controller: entry.value,
                decoration: InputDecoration(
                  labelText: entry.key,
                  isDense: true,
                ),
                onChanged: (_) {
                  widget.onSave({
                    for (final e in _controllers.entries) e.key: e.value.text,
                  });
                },
              ),
              const SizedBox(height: 8),
            ],
          ],
        ),
      ),
    );
  }
}
