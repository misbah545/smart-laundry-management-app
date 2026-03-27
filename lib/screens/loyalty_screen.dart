import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class LoyaltyScreen extends StatefulWidget {
  const LoyaltyScreen({super.key});

  @override
  State<LoyaltyScreen> createState() => _LoyaltyScreenState();
}

class _LoyaltyScreenState extends State<LoyaltyScreen> {
  final _orderId = TextEditingController(text: '1');
  final _points = TextEditingController(text: '100');
  bool _loading = false;
  Map<String, dynamic>? _result;

  @override
  void dispose() {
    _orderId.dispose();
    _points.dispose();
    super.dispose();
  }

  Future<void> _addPoints() async {
    setState(() => _loading = true);
    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    final res = await api.addLoyaltyPoints(int.tryParse(_orderId.text.trim()) ?? 1);
    setState(() {
      _result = res;
      _loading = false;
    });
  }

  Future<void> _redeemPoints() async {
    setState(() => _loading = true);
    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    final res = await api.redeemLoyaltyPoints(int.tryParse(_points.text.trim()) ?? 100);
    setState(() {
      _result = res;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Loyalty Points', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                TextField(
                  controller: _orderId,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Order ID'),
                ),
                const SizedBox(height: 8),
                PrimaryButton(label: 'Add Points', onPressed: _addPoints, loading: _loading),
                const SizedBox(height: 16),
                TextField(
                  controller: _points,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Points to Redeem'),
                ),
                const SizedBox(height: 8),
                PrimaryButton(label: 'Redeem Points', onPressed: _redeemPoints, loading: _loading),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (_result != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Result', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(_result.toString()),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
