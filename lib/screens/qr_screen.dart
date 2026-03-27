import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class QrScreen extends StatefulWidget {
  const QrScreen({super.key});

  @override
  State<QrScreen> createState() => _QrScreenState();
}

class _QrScreenState extends State<QrScreen> {
  final _orderId = TextEditingController(text: '1');
  bool _loading = false;
  Map<String, dynamic>? _result;

  @override
  void dispose() {
    _orderId.dispose();
    super.dispose();
  }

  Future<void> _generate() async {
    setState(() => _loading = true);
    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);

    final res = await api.generateQr(int.tryParse(_orderId.text.trim()) ?? 1);
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
        const Text('QR Code Generator', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
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
                const SizedBox(height: 12),
                PrimaryButton(label: 'Generate QR', onPressed: _generate, loading: _loading),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (_result != null && _result!['order_qr_code'] != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Order QR', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Center(
                    child: QrImageView(
                      data: _result!['order_qr_code'],
                      size: 180,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text('Clothes QR Codes', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      for (final cloth in (_result!['clothes_qr_codes'] ?? []))
                        Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            QrImageView(data: cloth['qr_code'], size: 90),
                            Text(cloth['cloth_type'] ?? 'Cloth'),
                          ],
                        ),
                    ],
                  ),
                ],
              ),
            ),
          )
      ],
    );
  }
}
