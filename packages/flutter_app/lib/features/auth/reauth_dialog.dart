import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/theme/app_colors.dart';

/// Shows a re-authentication dialog for sensitive actions.
/// Returns true if the user successfully re-authenticated.
Future<bool> showReauthDialog(BuildContext context, WidgetRef ref) async {
  final user = ref.read(currentUserProvider);
  if (user == null) return false;

  final isOAuth = user.appMetadata['provider'] != 'email';

  if (isOAuth) {
    // For OAuth users, just confirm intent
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirm Action'),
        content: const Text(
          'This is a sensitive action. Are you sure you want to continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Continue'),
          ),
        ],
      ),
    );
    return confirmed == true;
  }

  // For email/password users, ask for password
  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => _ReauthPasswordDialog(email: user.email ?? ''),
  );
  return result == true;
}

class _ReauthPasswordDialog extends ConsumerStatefulWidget {
  const _ReauthPasswordDialog({required this.email});
  final String email;

  @override
  ConsumerState<_ReauthPasswordDialog> createState() =>
      _ReauthPasswordDialogState();
}

class _ReauthPasswordDialogState
    extends ConsumerState<_ReauthPasswordDialog> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    final password = _controller.text;
    if (password.isEmpty) return;
    setState(() { _loading = true; _error = null; });
    try {
      await ref
          .read(authServiceProvider)
          .signInWithEmail(widget.email, password);
      if (mounted) Navigator.pop(context, true);
    } catch (_) {
      setState(() => _error = 'Incorrect password.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Enter your password'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Please re-enter your password to continue.'),
          const SizedBox(height: 16),
          TextField(
            controller: _controller,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Password',
              border: OutlineInputBorder(),
            ),
            onSubmitted: (_) => _verify(),
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: const TextStyle(color: AppColors.negative)),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _loading ? null : _verify,
          child: _loading
              ? const SizedBox(
                  width: 16, height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Confirm'),
        ),
      ],
    );
  }
}
