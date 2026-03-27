import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class QrVerificationScreen extends StatefulWidget {
  const QrVerificationScreen({super.key});

  @override
  State<QrVerificationScreen> createState() => _QrVerificationScreenState();
}

class _QrVerificationScreenState extends State<QrVerificationScreen> {
  final _qrController = TextEditingController();
  Map<String, dynamic>? _verifiedOrder;
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _verifyQr() async {
    if (_qrController.text.isEmpty) {
      setState(() => _errorMessage = 'Please enter or scan a QR code');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);

    try {
      final response = await client.verifyAdminQr(_qrController.text);
      if (mounted) {
        setState(() {
          _verifiedOrder = response;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Invalid QR code or order not found: $e';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Verify Orders via QR', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // QR Input Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Scan or Enter QR Code', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _qrController,
                      decoration: InputDecoration(
                        hintText: 'Enter QR code',
                        border: const OutlineInputBorder(),
                        suffixIcon: _qrController.text.isNotEmpty
                            ? IconButton(
                                icon: const Icon(Icons.clear),
                                onPressed: () {
                                  _qrController.clear();
                                  setState(() {
                                    _verifiedOrder = null;
                                    _errorMessage = '';
                                  });
                                },
                              )
                            : null,
                      ),
                      onChanged: (_) => setState(() {}),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isLoading ? null : _verifyQr,
                        icon: _isLoading ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ) : const Icon(Icons.check_circle),
                        label: Text(_isLoading ? 'Verifying...' : 'Verify QR'),
                      ),
                    ),
                  ],
                ),
            ),
            ),
            const SizedBox(height: 24),

            // Error Message
            if (_errorMessage.isNotEmpty)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: Colors.red.shade700),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _errorMessage,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Verified Order Details
            if (_verifiedOrder != null) ...[
              const SizedBox(height: 24),
              const Text('Order Details', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildDetailRow('Order ID', '#${_verifiedOrder!['id'] ?? 'N/A'}'),
                      const Divider(),
                      _buildDetailRow('Status', _verifiedOrder!['status'] ?? 'N/A'),
                      const Divider(),
                      _buildDetailRow('Customer', _verifiedOrder!['customer']?['username'] ?? 'N/A'),
                      const Divider(),
                      _buildDetailRow('Phone', _verifiedOrder!['customer']?['phone'] ?? 'N/A'),
                      const Divider(),
                      _buildDetailRow('Total Amount', '₹${_verifiedOrder!['total_amount']?.toStringAsFixed(2) ?? 'N/A'}'),
                    ],
                  ),
                ),
              ),

              // Clothes in Order
              const SizedBox(height: 24),
              const Text('Clothes in Order', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              if (_verifiedOrder!['clothes'] != null && (_verifiedOrder!['clothes'] as List).isNotEmpty)
                ...((_verifiedOrder!['clothes'] as List).map((cloth) {
                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: Colors.blue.shade100,
                        child: Text('${cloth['id']}'),
                      ),
                      title: Text('${cloth['cloth_type'] ?? 'Item'} - ${cloth['fabric'] ?? 'Unknown'}'),
                      subtitle: Text('QR: ${cloth['qr_code']?.substring(0, 8)}...'),
                      trailing: Icon(
                        Icons.check_circle,
                        color: Colors.green.shade600,
                      ),
                    ),
                  );
                }).toList())
              else
                Center(
                  child: Text(
                    'No clothes found',
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(color: Colors.grey.shade600)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    );
  }

  @override
  void dispose() {
    _qrController.dispose();
    super.dispose();
  }
}
