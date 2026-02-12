import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/theme/app_colors.dart';

class MfaSetupScreen extends ConsumerStatefulWidget {
  const MfaSetupScreen({super.key});

  @override
  ConsumerState<MfaSetupScreen> createState() => _MfaSetupScreenState();
}

class _MfaSetupScreenState extends ConsumerState<MfaSetupScreen> {
  String? _factorId;
  String? _qrUri;
  String? _secret;
  final _codeController = TextEditingController();
  bool _loading = false;
  String? _error;
  String? _success;
  List<dynamic> _factors = [];

  @override
  void initState() {
    super.initState();
    _loadFactors();
  }

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _loadFactors() async {
    try {
      final res = await ref.read(authServiceProvider).listMfaFactors();
      setState(() => _factors = res.totp);
    } catch (_) {}
  }

  Future<void> _enrollMfa() async {
    setState(() { _loading = true; _error = null; });
    try {
      final res = await ref.read(authServiceProvider).enrollMfa();
      setState(() {
        _factorId = res.id;
        _qrUri = res.totp?.qrCode;
        _secret = res.totp?.secret;
      });
    } catch (e) {
      setState(() => _error = 'Failed to set up MFA.');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _verifyMfa() async {
    final code = _codeController.text.trim();
    if (code.length != 6 || _factorId == null) return;
    setState(() { _loading = true; _error = null; });
    try {
      await ref.read(authServiceProvider).verifyMfa(_factorId!, code);
      setState(() {
        _success = 'MFA enabled successfully!';
        _qrUri = null;
        _secret = null;
        _factorId = null;
      });
      _codeController.clear();
      _loadFactors();
    } catch (e) {
      setState(() => _error = 'Invalid code. Please try again.');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _removeFactor(String factorId) async {
    try {
      await ref.read(authServiceProvider).unenrollMfa(factorId);
      _loadFactors();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('MFA removed')),
        );
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Two-Factor Authentication')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (_factors.isNotEmpty) ...[
            Text('Active Factors',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            for (final factor in _factors)
              Card(
                child: ListTile(
                  leading: const Icon(Icons.verified_user, color: AppColors.positive),
                  title: Text('TOTP (${factor.id.substring(0, 8)}…)'),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppColors.negative),
                    onPressed: () => _removeFactor(factor.id),
                  ),
                ),
              ),
            const SizedBox(height: 24),
          ],

          if (_qrUri == null && _success == null)
            FilledButton.icon(
              onPressed: _loading ? null : _enrollMfa,
              icon: const Icon(Icons.qr_code),
              label: const Text('Set Up Authenticator App'),
            ),

          if (_qrUri != null) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(children: [
                  const Text(
                    'Scan this QR code with your authenticator app:',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  // QR code would be rendered here — for now show the URI
                  Center(
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'QR Code\n(Use URI below)',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.black54),
                      ),
                    ),
                  ),
                  if (_secret != null) ...[
                    const SizedBox(height: 12),
                    Text('Manual entry key:', style: TextStyle(color: AppColors.textSecondary)),
                    const SizedBox(height: 4),
                    SelectableText(
                      _secret!,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  TextField(
                    controller: _codeController,
                    decoration: const InputDecoration(
                      labelText: '6-digit code',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => _verifyMfa(),
                  ),
                  const SizedBox(height: 8),
                  FilledButton(
                    onPressed: _loading ? null : _verifyMfa,
                    child: _loading
                        ? const SizedBox(
                            width: 20, height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2))
                        : const Text('Verify & Enable'),
                  ),
                ],
              ),
            ),
          ],

          if (_error != null) ...[
            const SizedBox(height: 16),
            Text(_error!, style: const TextStyle(color: AppColors.negative)),
          ],
          if (_success != null) ...[
            const SizedBox(height: 16),
            Text(_success!, style: const TextStyle(color: AppColors.positive)),
          ],
        ],
      ),
    );
  }
}
