import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  String _reportType = 'daily';
  Map<String, dynamic> analytics = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    
    try {
      final response = await client.getAdminAnalytics(_reportType);
      if (mounted) {
        setState(() {
          analytics = response;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading analytics: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Reports & Analytics', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Report Type Selector
                  const Text('Report Type', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(label: Text('Daily'), value: 'daily'),
                      ButtonSegment(label: Text('Weekly'), value: 'weekly'),
                      ButtonSegment(label: Text('Monthly'), value: 'monthly'),
                    ],
                    selected: {_reportType},
                    onSelectionChanged: (value) {
                      setState(() => _reportType = value.first);
                      _loadAnalytics();
                    },
                  ),
                  const SizedBox(height: 32),

                  // Summary Stats Grid
                  const Text('Summary Statistics', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    children: [
                      _statCard('Total Orders', '${analytics['total_orders'] ?? 0}', Colors.blue, Icons.shopping_bag),
                      _statCard('Revenue', '₹${analytics['revenue']?.toStringAsFixed(0) ?? 0}', Colors.green, Icons.attach_money),
                      _statCard('Avg Order Value', '₹${analytics['avg_order_value']?.toStringAsFixed(0) ?? 0}', Colors.purple, Icons.trending_up),
                      _statCard('Complaints', '${analytics['complaints'] ?? 0}', Colors.orange, Icons.warning),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Service Breakdown
                  if (analytics['service_breakdown'] != null)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Service Breakdown', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 12),
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              children: (analytics['service_breakdown'] as List?)
                                      ?.map<Widget>((service) {
                                    return Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(service['service_type'] ?? 'Unknown'),
                                          Chip(
                                            label: Text('${service['count'] ?? 0} orders'),
                                            backgroundColor: Colors.blue.shade100,
                                          ),
                                        ],
                                      ),
                                    );
                                  }).toList() ??
                                  [],
                            ),
                          ),
                        ),
                        const SizedBox(height: 32),
                      ],
                    ),

                  // Refund/Discount Management
                  const Text('Refund & Discount Management', 
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          ListTile(
                            title: const Text('Total Refunds'),
                            trailing: Text(
                              '₹${analytics['total_refunds']?.toStringAsFixed(0) ?? 0}',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                          ),
                          const Divider(),
                          ListTile(
                            title: const Text('Total Discounts Applied'),
                            trailing: Text(
                              '₹${analytics['total_discounts']?.toStringAsFixed(0) ?? 0}',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _statCard(String title, String value, Color color, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                Icon(icon, color: color, size: 20),
              ],
            ),
            Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
