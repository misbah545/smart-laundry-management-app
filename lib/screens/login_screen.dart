import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _password = TextEditingController();
  final _baseUrl = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    _baseUrl.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
    });

    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl);

    if (_baseUrl.text.trim().isNotEmpty) {
      await appState.setBaseUrl(_baseUrl.text.trim());
    }

    final response = await api.login(_username.text.trim(), _password.text.trim());
    
    if (response['access'] != null) {
      final userType = response['user_type'] as String?;
      final username = response['username'] as String?;
      final userId = response['user_id'] as int?;
      
      // Accept ADMIN or CUSTOMER users
      if (userType != 'ADMIN' && userType != 'CUSTOMER') {
        setState(() {
          _error = 'Invalid account type: $userType';
          _loading = false;
        });
        return;
      }
      
      // Save session with full user data
      await appState.setSession(
        response['access'] as String,
        userType ?? 'UNKNOWN',
        username ?? 'Unknown',
        userId ?? 0,
      );
    } else {
      setState(() {
        _error = response['error']?.toString() ?? 'Login failed.';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();
    _baseUrl.text = appState.baseUrl;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF2B6CB0), Color(0xFF38B2AC)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        'Smart Laundry',
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _baseUrl,
                        decoration: const InputDecoration(
                          labelText: 'API Base URL',
                          hintText: 'http://127.0.0.1:8000',
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _username,
                        decoration: const InputDecoration(labelText: 'Username'),
                        validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _password,
                        decoration: const InputDecoration(labelText: 'Password'),
                        obscureText: true,
                        validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                      ),
                      const SizedBox(height: 16),
                      if (_error != null) ...[
                        Text(_error!, style: const TextStyle(color: Colors.red)),
                        const SizedBox(height: 8),
                      ],
                      PrimaryButton(
                        label: 'Login',
                        onPressed: _login,
                        loading: _loading,
                      ),
                      const SizedBox(height: 8),
                      const Text('Use admin / admin123 for demo'),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
