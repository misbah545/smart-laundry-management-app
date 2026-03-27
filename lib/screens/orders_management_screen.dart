import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class OrdersManagementScreen extends StatefulWidget {
  const OrdersManagementScreen({super.key});

  @override
  State<OrdersManagementScreen> createState() => _OrdersManagementScreenState();
}

class _OrdersManagementScreenState extends State<OrdersManagementScreen> {
  List<dynamic> orders = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    
    try {
      final response = await client.getAdminOrders();
      if (response['error'] != null) {
        if (mounted) {
          setState(() => _isLoading = false);
          final message = (response['error'] is Map<String, dynamic>)
              ? (response['error']['message'] ?? response['error'].toString())
              : response['error'].toString();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error loading orders: $message'), backgroundColor: Colors.red),
          );
        }
        return;
      }
      if (mounted) {
        setState(() {
          orders = response['orders'] ?? [];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading orders: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Order Status Updates', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : orders.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.shopping_bag_outlined, size: 64, color: Colors.grey.shade400),
                      const SizedBox(height: 16),
                      Text('No orders found', style: TextStyle(color: Colors.grey.shade600)),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: orders.length,
                  itemBuilder: (context, index) {
                    final order = orders[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.blue.shade100,
                          child: Text('#${order['id']}', style: const TextStyle(fontSize: 10)),
                        ),
                        title: Text('Order #${order['id']}'),
                        subtitle: Text('Status: ${order['status'] ?? 'PENDING'}'),
                        trailing: PopupMenuButton<String>(
                          onSelected: (status) async {
                            final appState = context.read<AppState>();
                            final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
                            try {
                              await client.updateAdminOrderStatus(order['id'], status);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Status updated to $status'), backgroundColor: Colors.green),
                              );
                              _loadOrders();
                            } catch (e) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                              );
                            }
                          },
                          itemBuilder: (BuildContext context) => [
                            for (final status in ['PENDING', 'ASSIGNED', 'PICKED', 'IN_PROCESS', 'DELIVERED', 'CANCELLED'])
                              PopupMenuItem<String>(
                                value: status,
                                child: Text(status),
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
