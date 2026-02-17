import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/settings_provider.dart';
import 'features/auth/login_screen.dart';
import 'features/auth/signup_screen.dart';
import 'features/auth/profile_screen.dart';
import 'features/auth/mfa_setup_screen.dart';
import 'features/auth/account_settings_screen.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/alerts/alerts_screen.dart';
import 'features/scenarios/scenarios_screen.dart';
import 'features/settings/settings_screen.dart';
import 'features/tax_breakdown/tax_breakdown_screen.dart';
import 'features/onboarding/onboarding_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

/// Routes that require authentication.
const _protectedPaths = {'/alerts', '/scenarios', '/profile', '/mfa-setup', '/account-settings'};

final routerProvider = Provider<GoRouter>((ref) {
  final settings = ref.watch(settingsProvider);
  final isAuthenticated = ref.watch(isAuthenticatedProvider);
  final supabaseAvailable = ref.watch(supabaseAvailableProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: settings.onboardingComplete ? '/' : '/onboarding',
    redirect: (context, state) {
      final path = state.uri.path;

      // If Supabase isn't configured, skip all auth redirects (anonymous mode)
      if (!supabaseAvailable) return null;

      // Allow unauthenticated access to login, signup, onboarding, dashboard
      const publicPaths = {'/login', '/signup', '/onboarding', '/', '/breakdown'};
      if (publicPaths.contains(path)) {
        // If authenticated and on login/signup, redirect to dashboard
        if (isAuthenticated && (path == '/login' || path == '/signup')) {
          return '/';
        }
        return null;
      }

      // Protected routes require auth
      if (_protectedPaths.contains(path) && !isAuthenticated) {
        return '/login';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/onboarding',
        builder: (_, __) => const OnboardingScreen(),
      ),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/signup', builder: (_, __) => const SignupScreen()),
      GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      GoRoute(path: '/mfa-setup', builder: (_, __) => const MfaSetupScreen()),
      GoRoute(path: '/account-settings', builder: (_, __) => const AccountSettingsScreen()),
      ShellRoute(
        builder: (context, state, child) => _ScaffoldWithNav(child: child),
        routes: [
          GoRoute(path: '/', builder: (_, __) => const DashboardScreen()),
          GoRoute(path: '/alerts', builder: (_, __) => const AlertsScreen()),
          GoRoute(
              path: '/scenarios',
              builder: (_, __) => const ScenariosScreen()),
          GoRoute(
              path: '/settings', builder: (_, __) => const SettingsScreen()),
        ],
      ),
      GoRoute(
          path: '/breakdown',
          builder: (_, __) => const TaxBreakdownScreen()),
    ],
  );
});

class _ScaffoldWithNav extends StatelessWidget {
  const _ScaffoldWithNav({required this.child});
  final Widget child;

  int _indexOf(String location) {
    if (location.startsWith('/alerts')) return 1;
    if (location.startsWith('/scenarios')) return 2;
    if (location.startsWith('/settings')) return 3;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _indexOf(location),
        onDestinationSelected: (i) {
          const paths = ['/', '/alerts', '/scenarios', '/settings'];
          context.go(paths[i]);
        },
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.dashboard_outlined),
              selectedIcon: Icon(Icons.dashboard),
              label: 'Dashboard'),
          NavigationDestination(
              icon: Icon(Icons.lightbulb_outline),
              selectedIcon: Icon(Icons.lightbulb),
              label: 'Tax Tips'),
          NavigationDestination(
              icon: Icon(Icons.explore_outlined),
              selectedIcon: Icon(Icons.explore),
              label: 'What If'),
          NavigationDestination(
              icon: Icon(Icons.settings_outlined),
              selectedIcon: Icon(Icons.settings),
              label: 'Settings'),
        ],
      ),
    );
  }
}
