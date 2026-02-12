import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/alerts/alerts_screen.dart';
import 'features/scenarios/scenarios_screen.dart';
import 'features/settings/settings_screen.dart';
import 'features/tax_breakdown/tax_breakdown_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

final router = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/',
  routes: [
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
    final location =
        GoRouterState.of(context).uri.toString();
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
              icon: Icon(Icons.warning_amber_outlined),
              selectedIcon: Icon(Icons.warning),
              label: 'Alerts'),
          NavigationDestination(
              icon: Icon(Icons.compare_arrows_outlined),
              selectedIcon: Icon(Icons.compare_arrows),
              label: 'Scenarios'),
          NavigationDestination(
              icon: Icon(Icons.settings_outlined),
              selectedIcon: Icon(Icons.settings),
              label: 'Settings'),
        ],
      ),
    );
  }
}
