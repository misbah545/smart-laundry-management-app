import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class PriceScreen extends StatefulWidget {
  const PriceScreen({super.key});

  @override
  State<PriceScreen> createState() => _PriceScreenState();
}

class _PriceScreenState extends State<PriceScreen> {
  final _formKey = GlobalKey<FormState>();
  final _clothType = TextEditingController(text: 'Shirt');
  final _fabric = TextEditingController(text: 'SILK');
  final _serviceType = TextEditingController(text: 'DRY_CLEAN');
  final _weight = TextEditingController(text: '0.5');

  bool _loading = false;
  Map<String, dynamic>? _result;

  @override
  void dispose() {
    _clothType.dispose();
    _fabric.dispose();
    _serviceType.dispose();
    _weight.dispose();
    super.dispose();
  }

  Future<void> _estimate() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);

    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);

    final res = await api.estimatePrice(
      clothType: _clothType.text.trim(),
      fabric: _fabric.text.trim(),
      serviceType: _serviceType.text.trim(),
      weight: double.tryParse(_weight.text.trim()) ?? 0.5,
    );

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
        const Text('ML Price Estimation', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _clothType,
                    decoration: const InputDecoration(labelText: 'Cloth Type'),
                    validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _fabric,
                    decoration: const InputDecoration(labelText: 'Fabric (COTTON/SILK/WOOL)'),
                    validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _serviceType,
                    decoration: const InputDecoration(labelText: 'Service Type (DRY_CLEAN/WASH)'),
                    validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _weight,
                    decoration: const InputDecoration(labelText: 'Weight (kg)'),
                    keyboardType: TextInputType.number,
                    validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  PrimaryButton(label: 'Estimate Price', onPressed: _estimate, loading: _loading),
                ],
              ),
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
                  Text('Estimated Price: ${_result!['estimated_price'] ?? 'N/A'}'),
                  Text('Confidence: ${_result!['confidence'] ?? 'N/A'}'),
                  if (_result!['message'] != null) Text('Message: ${_result!['message']}'),
                ],
              ),
            ),
          )
      ],
    );
  }
}
