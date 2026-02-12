import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'router.dart';

class TaxLensApp extends StatelessWidget {
  const TaxLensApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'TaxLens',
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.dark,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
