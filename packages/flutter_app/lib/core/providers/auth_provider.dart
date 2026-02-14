import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const _webRedirect = 'https://taxlens.ziziou.com';
const _nativeRedirect = 'com.taxlens.app://callback';

/// Whether Supabase is initialized and available.
final supabaseAvailableProvider = StateProvider<bool>((ref) => false);

/// Stream of Supabase auth state changes.
final authStateProvider = StreamProvider<AuthState>((ref) {
  final available = ref.watch(supabaseAvailableProvider);
  if (!available) return const Stream.empty();
  return Supabase.instance.client.auth.onAuthStateChange;
});

/// Current Supabase user (null if not logged in or Supabase not configured).
final currentUserProvider = Provider<User?>((ref) {
  final available = ref.watch(supabaseAvailableProvider);
  if (!available) return null;
  return Supabase.instance.client.auth.currentUser;
});

/// Whether the user is authenticated.
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(currentUserProvider) != null;
});

/// Current session (for JWT access).
final currentSessionProvider = Provider<Session?>((ref) {
  final available = ref.watch(supabaseAvailableProvider);
  if (!available) return null;
  return Supabase.instance.client.auth.currentSession;
});

/// Auth service for performing auth operations.
class AuthService {
  AuthService(this._ref);
  final Ref _ref;

  bool get _available => _ref.read(supabaseAvailableProvider);
  GoTrueClient? get _auth =>
      _available ? Supabase.instance.client.auth : null;

  Future<AuthResponse> signInWithEmail(String email, String password) async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.signInWithPassword(email: email, password: password);
  }

  Future<AuthResponse> signUpWithEmail(String email, String password) async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.signUp(email: email, password: password);
  }

  Future<void> signInWithGoogle() async {
    if (_auth == null) throw Exception('Supabase not configured');
    await _auth!.signInWithOAuth(
      OAuthProvider.google,
      redirectTo: kIsWeb ? _webRedirect : _nativeRedirect,
    );
  }

  Future<void> signInWithApple() async {
    if (_auth == null) throw Exception('Supabase not configured');
    await _auth!.signInWithOAuth(
      OAuthProvider.apple,
      redirectTo: kIsWeb ? _webRedirect : _nativeRedirect,
    );
  }

  Future<void> signInWithMagicLink(String email) async {
    if (_auth == null) throw Exception('Supabase not configured');
    await _auth!.signInWithOtp(
      email: email,
      emailRedirectTo: kIsWeb ? _webRedirect : _nativeRedirect,
    );
  }

  Future<void> resetPassword(String email) async {
    if (_auth == null) throw Exception('Supabase not configured');
    await _auth!.resetPasswordForEmail(
      email,
      redirectTo: kIsWeb ? '$_webRedirect/reset-callback' : 'com.taxlens.app://reset-callback',
    );
  }

  Future<UserResponse> updateEmail(String email) async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.updateUser(UserAttributes(email: email));
  }

  Future<UserResponse> updatePassword(String password) async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.updateUser(UserAttributes(password: password));
  }

  Future<AuthMFAEnrollResponse> enrollMfa() async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.mfa.enroll(factorType: FactorType.totp);
  }

  Future<AuthMFAVerifyResponse> verifyMfa(
      String factorId, String code) async {
    if (_auth == null) throw Exception('Supabase not configured');
    final challenge =
        await _auth!.mfa.challenge(factorId: factorId);
    return _auth!.mfa.verify(
      factorId: factorId,
      challengeId: challenge.id,
      code: code,
    );
  }

  Future<AuthMFAUnenrollResponse> unenrollMfa(String factorId) async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.mfa.unenroll(factorId);
  }

  Future<AuthMFAListFactorsResponse> listMfaFactors() async {
    if (_auth == null) throw Exception('Supabase not configured');
    return _auth!.mfa.listFactors();
  }

  Future<void> signOut() async {
    if (_auth == null) return;
    await _auth!.signOut();
  }
}

final authServiceProvider = Provider<AuthService>((ref) => AuthService(ref));
