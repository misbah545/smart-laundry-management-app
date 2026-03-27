import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class InventoryScreen extends StatefulWidget {
  const InventoryScreen({super.key});

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen> {
  bool _loading = false;
  Map<String, dynamic>? _result;

  Future<void> _load() async {
    setState(() => _loading = true);
    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    final res = await api.checkInventory();

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
        const Text('Inventory', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        PrimaryButton(label: 'Check Inventory', onPressed: _load, loading: _loading),
        const SizedBox(height: 12),
        if (_result != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Total Items: ${_result!['total_items'] ?? 0}'),
                  Text('Low Stock Count: ${_result!['low_stock_count'] ?? 0}'),
                  const SizedBox(height: 8),
                  if ((_result!['low_stock_items'] ?? []).isEmpty)
                    const Text('No low stock items.')
                  else
                    for (final item in _result!['low_stock_items'])
                      Text('• ${item['item_name']} (${item['quantity']} left)'),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
