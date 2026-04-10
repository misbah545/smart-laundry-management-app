import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class WorkloadScreen extends StatefulWidget {
  const WorkloadScreen({super.key});

  @override
  State<WorkloadScreen> createState() => _WorkloadScreenState();
}

class _WorkloadScreenState extends State<WorkloadScreen> {
  bool _loading = false;
  List<dynamic> _predictions = [];

  Future<void> _load() async {
    setState(() => _loading = true);
    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    final res = await api.predictWorkload();

    setState(() {
      _predictions = res['predictions'] ?? [];
      _loading = false;
    });
  }

  String _formatDate(String date) {
    try {
      final dt = DateTime.parse(date);
      return DateFormat('EEE, MMM d').format(dt);
    } catch (_) {
      return date;
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('AI Workload Prediction', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        PrimaryButton(label: 'Load Predictions', onPressed: _load, loading: _loading),
        const SizedBox(height: 12),
        for (final p in _predictions)
          Card(
            child: ListTile(
              title: Text(_formatDate(p['date'] ?? '')),
              subtitle: Text('Workload: ${p['workload'] ?? 'N/A'}'),
              trailing: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Orders: ${p['predicted_orders'] ?? 0}'),
                  Text('Staff: ${p['staff_recommendation'] ?? 0}'),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
