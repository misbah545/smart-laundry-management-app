import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class DataDashboardScreen extends StatefulWidget {
  const DataDashboardScreen({super.key});

  @override
  State<DataDashboardScreen> createState() => _DataDashboardScreenState();
}

class _DataDashboardScreenState extends State<DataDashboardScreen> {
  int _selectedTab = 0; // 0: Orders, 1: Drivers, 2: Inventory, 3: Complaints
  bool _isLoading = false;
  
  // Data storage
  List<dynamic> orders = [];
  List<dynamic> drivers = [];
  List<dynamic> inventory = [];
  List<dynamic> complaints = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    
    setState(() => _isLoading = true);
    
    try {
      // Load all data in parallel
      final inventoryResp = await client.getAdminInventory();
      final complaintsResp = await client.getAdminComplaints('OPEN');
      final ordersResp = await client.getAdminOrders();
      
      if (mounted) {
        setState(() {
          orders = ordersResp['orders'] ?? [];
          inventory = inventoryResp['inventory'] ?? [];
          complaints = complaintsResp['complaints'] ?? [];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📊 Real Database Tables'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.blue.shade700,
      ),
      body: Column(
        children: [
          // Tab Selector
          Container(
            padding: const EdgeInsets.all(12),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildTabButton('📦 Orders', 0),
                  _buildTabButton('👨‍💼 Drivers', 1),
                  _buildTabButton('📦 Inventory', 2),
                  _buildTabButton('⚠️ Complaints', 3),
                ],
              ),
            ),
          ),
          
          // Content
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _buildTabContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton(String label, int index) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 6),
      child: ElevatedButton(
        onPressed: () => setState(() => _selectedTab = index),
        style: ElevatedButton.styleFrom(
          backgroundColor: _selectedTab == index ? Colors.blue.shade700 : Colors.grey.shade300,
          foregroundColor: _selectedTab == index ? Colors.white : Colors.black,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
        child: Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _buildTabContent() {
    switch (_selectedTab) {
      case 0:
        return _buildOrdersTable();
      case 1:
        return _buildDriversTable();
      case 2:
        return _buildInventoryTable();
      case 3:
        return _buildComplaintsTable();
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildOrdersTable() {
    if (orders.isEmpty) return const Center(child: Text('No orders found'));
    
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: orders.length,
      itemBuilder: (context, i) {
        final order = orders[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Order #${order['id']}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: _getStatusColor(order['status']),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        order['status'] ?? 'UNKNOWN',
                        style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text('Customer: ${order['customer']['username'] ?? 'N/A'}', style: const TextStyle(fontSize: 12)),
                Text('Amount: ₹${order['total_amount'] ?? 0}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.green)),
                Text('Date: ${order['order_date']?.toString().split('T')[0] ?? 'N/A'}', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                if (order['driver'] != null) 
                  Text('Driver: ${order['driver']['username']}', style: const TextStyle(fontSize: 11, color: Colors.blue)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildDriversTable() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.construction, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          const Text('👉 Go to "Driver Management"', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('tab from drawer to manage drivers', style: TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildInventoryTable() {
    if (inventory.isEmpty) return const Center(child: Text('No inventory items found'));
    
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: inventory.length,
      itemBuilder: (context, i) {
        final item = inventory[i];
        final isLowStock = (item['quantity'] ?? 0) <= (item['min_threshold'] ?? 10);
        
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          borderOnForeground: isLowStock,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        item['item_name'] ?? 'Unknown',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                    if (isLowStock)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: Colors.red.shade100, borderRadius: BorderRadius.circular(8)),
                        child: const Text('⚠️ LOW', style: TextStyle(color: Colors.red, fontSize: 10, fontWeight: FontWeight.bold)),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Text('Quantity: ${item['quantity'] ?? 0} ${item['unit'] ?? 'units'} (Min: ${item['min_threshold'] ?? 0})', 
                  style: const TextStyle(fontSize: 12)),
                Text('Category: ${item['category'] ?? 'N/A'}', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                Text('Price: ₹${item['price_per_unit'] ?? 0}', style: const TextStyle(fontSize: 11, color: Colors.green, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildComplaintsTable() {
    if (complaints.isEmpty) return const Center(child: Text('No complaints found'));
    
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: complaints.length,
      itemBuilder: (context, i) {
        final complaint = complaints[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Complaint #${complaint['id']}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: complaint['status'] == 'RESOLVED' ? Colors.green.shade100 : Colors.orange.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        complaint['status'] ?? 'UNKNOWN',
                        style: TextStyle(
                          color: complaint['status'] == 'RESOLVED' ? Colors.green : Colors.orange,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text('Type: ${complaint['issue_type'] ?? 'N/A'}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                Text('Description: ${complaint['description'] ?? ''}', 
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _getStatusColor(String? status) {
    switch (status) {
      case 'PENDING':
        return Colors.orange;
      case 'ASSIGNED':
        return Colors.blue;
      case 'PICKED':
        return Colors.purple;
      case 'IN_PROCESS':
        return Colors.indigo;
      case 'DELIVERED':
        return Colors.green;
      case 'CANCELLED':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
