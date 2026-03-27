import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class CustomerLoyaltyScreen extends StatefulWidget {
  const CustomerLoyaltyScreen({super.key});

  @override
  State<CustomerLoyaltyScreen> createState() => _CustomerLoyaltyScreenState();
}

class _CustomerLoyaltyScreenState extends State<CustomerLoyaltyScreen> {
  List<dynamic> customers = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadCustomers();
  }

  Future<void> _loadCustomers() async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    
    try {
      final response = await client.getAdminLoyaltyTracking();
      if (mounted) {
        setState(() {
          customers = response['customers'] ?? [];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading customer data: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Customer Loyalty Tracking', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : customers.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.people_outline, size: 64, color: Colors.grey.shade400),
                      const SizedBox(height: 16),
                      Text('No customers found', style: TextStyle(color: Colors.grey.shade600)),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: customers.length,
                  itemBuilder: (context, index) {
                    final customer = customers[index];
                    final points = customer['loyalty_points'] ?? 0;
                    final tier = points >= 1000 ? 'Gold' : points >= 500 ? 'Silver' : 'Bronze';
                    final tierColor = tier == 'Gold' 
                        ? Colors.amber 
                        : tier == 'Silver' 
                        ? Colors.grey.shade400 
                        : Colors.orange.shade700;

                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        customer['username'] ?? 'Unknown',
                                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                      ),
                                      Text(
                                        customer['email'] ?? 'N/A',
                                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                                      ),
                                    ],
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: tierColor.withValues(alpha: 0.2),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(color: tierColor),
                                  ),
                                  child: Row(
                                    children: [
                                      Icon(Icons.star, size: 16, color: tierColor),
                                      const SizedBox(width: 4),
                                      Text(tier, style: TextStyle(color: tierColor, fontWeight: FontWeight.bold)),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            // Stats Row
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                _statWidget('Orders', '${customer['total_orders'] ?? 0}', Colors.blue),
                                _statWidget('Spent', '₹${customer['total_spent']?.toStringAsFixed(0) ?? 0}', Colors.green),
                                _statWidget('Points', '${customer['loyalty_points'] ?? 0}', Colors.purple),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }

  Widget _statWidget(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }
}
