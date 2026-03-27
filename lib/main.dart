import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/app_state.dart';
import 'screens/admin_dashboard_screen.dart';
import 'screens/customer_dashboard_screen.dart';
import 'screens/login_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const SmartLaundryApp());
}

class SmartLaundryApp extends StatelessWidget {
  const SmartLaundryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState()..loadFromStorage(),
      child: MaterialApp(
        title: 'Smart Laundry',
        theme: AppTheme.light(),
        home: const AppEntry(),
      ),
    );
  }
}

class AppEntry extends StatelessWidget {
  const AppEntry({super.key});

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();
    
    if (!appState.isAuthenticated) {
      return const LoginScreen();
    }
    
    // Route based on user type
    if (appState.isAdmin) {
      return const AdminDashboardScreen();
    } else {
      return const CustomerDashboardScreen();
    }
  }
}
