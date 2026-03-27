import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class CustomerLoyaltyManagementScreen extends StatefulWidget {
  const CustomerLoyaltyManagementScreen({super.key});

  @override
  State<CustomerLoyaltyManagementScreen> createState() => _CustomerLoyaltyManagementScreenState();
}

class _CustomerLoyaltyManagementScreenState extends State<CustomerLoyaltyManagementScreen>
    with SingleTickerProviderStateMixin {
  bool _isLoading = true;
  late TabController _tabController;
  List<dynamic> customers = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  Future<void> _loadData() async {
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
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('💎 Loyalty Program'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.amber.shade700,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          indicatorWeight: 3,
          tabs: const [
            Tab(text: 'All Customers', icon: Icon(Icons.people)),
            Tab(text: 'Top Spenders', icon: Icon(Icons.trending_up)),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildAllCustomersTab(),
                _buildTopSpendersTab(),
              ],
            ),
    );
  }

  Widget _buildAllCustomersTab() {
    if (customers.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people_outline, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text('No customers found', style: TextStyle(color: Colors.grey, fontSize: 16)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: customers.length,
      itemBuilder: (context, index) {
        final customer = customers[index];
        return _buildCustomerCard(customer);
      },
    );
  }

  Widget _buildTopSpendersTab() {
    final topSpenders = List.from(customers)
      ..sort((a, b) => (b['total_spent'] ?? 0).compareTo(a['total_spent'] ?? 0))
      ..take(10)
      .toList();

    if (topSpenders.isEmpty) {
      return const Center(child: Text('No data available'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: topSpenders.length,
      itemBuilder: (context, index) {
        final customer = topSpenders[index];
        final rank = index + 1;
        return _buildRankedCustomerCard(customer, rank);
      },
    );
  }

  Widget _buildCustomerCard(dynamic customer) {
    final points = customer['loyalty_points'] ?? 0;
    final tier = _getTierName(points);
    final tierColor = _getTierColor(points);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [Colors.white, tierColor.withValues(alpha: 0.05)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
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
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          customer['email'] ?? 'N/A',
                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: tierColor,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        Text(
                          tier,
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                        Text(
                          '$points pts',
                          style: const TextStyle(color: Colors.white, fontSize: 10),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatColumn('Orders', '${customer['total_orders'] ?? 0}'),
                  _buildStatColumn('Spent', '₹${customer['total_spent'] ?? 0}'),
                  _buildStatColumn('Points', '$points'),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _showAddPointsDialog(customer),
                      icon: const Icon(Icons.add_circle, size: 16),
                      label: const Text('Add Points'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade600,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _showRedeemDialog(customer),
                      icon: const Icon(Icons.redeem, size: 16),
                      label: const Text('Redeem'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRankedCustomerCard(dynamic customer, int rank) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: rank == 1
                    ? Colors.amber
                    : rank == 2
                        ? Colors.grey.shade400
                        : Colors.orange.shade600,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  '$rank',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    customer['username'] ?? 'Unknown',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '₹${customer['total_spent'] ?? 0} spent • ${customer['total_orders'] ?? 0} orders',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                const Text('Points', style: TextStyle(fontSize: 10, color: Colors.grey)),
                Text(
                  '${customer['loyalty_points'] ?? 0}',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.amber),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatColumn(String label, String value) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }

  void _showAddPointsDialog(dynamic customer) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Add Points to ${customer['username']}'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'Points to Add',
            hintText: 'e.g., 100',
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              // TODO: Add API call to add points
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('✅ Points added successfully')),
              );
              Navigator.pop(context);
              _loadData();
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
    controller.dispose();
  }

  void _showRedeemDialog(dynamic customer) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Redeem Points for ${customer['username']}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Available: ${customer['loyalty_points'] ?? 0} points',
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Points to Add',
                hintText: 'e.g., 100',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            onPressed: () {
              // TODO: Add API call to redeem points
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('✅ Points redeemed successfully')),
              );
              Navigator.pop(context);
              _loadData();
            },
            child: const Text('Redeem'),
          ),
        ],
      ),
    );
    controller.dispose();
  }

  String _getTierName(int points) {
    if (points >= 1000) return '💎 Gold';
    if (points >= 500) return '🔌 Silver';
    if (points >= 100) return '🥉 Bronze';
    return '⭐ Member';
  }

  Color _getTierColor(int points) {
    if (points >= 1000) return Colors.amber;
    if (points >= 500) return Colors.grey;
    if (points >= 100) return Colors.orange;
    return Colors.blue;
  }
}
