import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class CustomerDashboardScreen extends StatefulWidget {
  const CustomerDashboardScreen({super.key});

  @override
  State<CustomerDashboardScreen> createState() => _CustomerDashboardScreenState();
}

class _CustomerDashboardScreenState extends State<CustomerDashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final appState = AppState();
  
  bool _isLoading = true;
  double totalSpent = 0.0;
  int totalOrders = 0;
  int loyaltyPoints = 0;
  int pendingOrders = 0;

  List<dynamic> myOrders = [];
  List<dynamic> notifications = [];
  Map<String, dynamic> userProfile = {};

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadCustomerData();
  }

  Future<void> _loadCustomerData() async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    
    setState(() => _isLoading = true);
    
    try {
      final [ordersResp, notificationsResp] = await Future.wait([
        client.getCustomerOrders(),
        client.getNotifications(),
      ]);
      
      if (mounted) {
        setState(() {
          myOrders = ordersResp['orders'] ?? [];
          totalOrders = myOrders.length;
          totalSpent = myOrders.fold(0.0, (sum, order) => sum + (order['total_amount'] as num? ?? 0)).toDouble();
          pendingOrders = myOrders.where((o) => o['status'] != 'DELIVERED' && o['status'] != 'CANCELLED').length;
          
          notifications = notificationsResp['notifications'] ?? [];
          
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
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('👕 My Laundry Dashboard'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.blue.shade600,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadCustomerData,
          ),
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('${notifications.length} notifications')),
              );
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                children: [
                  // KPI Cards
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: isMobile ? 2 : 4,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      children: [
                        _buildKPICard('📦 Total Orders', '$totalOrders', Colors.blue),
                        _buildKPICard('⏳ Pending', '$pendingOrders', Colors.orange),
                        _buildKPICard('💰 Total Spent', '₹${totalSpent.toStringAsFixed(2)}', Colors.green),
                        _buildKPICard('💎 Loyalty Points', '$loyaltyPoints', Colors.amber),
                      ],
                    ),
                  ),

                  // Tab Navigation
                  TabBar(
                    controller: _tabController,
                    indicatorColor: Colors.blue,
                    labelColor: Colors.blue,
                    unselectedLabelColor: Colors.grey,
                    tabs: const [
                      Tab(icon: Icon(Icons.shopping_bag), text: 'My Orders'),
                      Tab(icon: Icon(Icons.local_shipping), text: 'Tracking'),
                      Tab(icon: Icon(Icons.notifications), text: 'Alerts'),
                      Tab(icon: Icon(Icons.person), text: 'Profile'),
                    ],
                  ),

                  // Tab Content
                  SizedBox(
                    height: 500,
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        _buildMyOrdersTab(),
                        _buildTrackingTab(),
                        _buildAlertsTab(),
                        _buildProfileTab(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildKPICard(String label, String value, Color color) {
    return Card(
      elevation: 2,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [color.withValues(alpha: 0.1), color.withValues(alpha: 0.05)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w600)),
              Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMyOrdersTab() {
    if (myOrders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.shopping_bag_outlined, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text('No orders yet', style: TextStyle(color: Colors.grey, fontSize: 16)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: myOrders.length,
      itemBuilder: (context, i) {
        final order = myOrders[i];
        return _buildOrderCard(order);
      },
    );
  }

  Widget _buildOrderCard(dynamic order) {
    final statusColor = _getStatusColor(order['status']);
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Order #${order['id']}',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    order['status'] ?? 'UNKNOWN',
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Amount', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                    Text('₹${order['total_amount'] ?? 0}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.green)),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Clothes', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                    Text('${order['clothes_count'] ?? 0} items', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Date', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                    Text(
                      order['order_date']?.toString().split('T')[0] ?? 'N/A',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _showOrderDetails(order),
                    icon: const Icon(Icons.visibility, size: 16),
                    label: const Text('View Details'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade600,
                      padding: const EdgeInsets.symmetric(vertical: 8),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _trackOrder(order['id']),
                    icon: const Icon(Icons.location_on, size: 16),
                    label: const Text('Track'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrackingTab() {
    if (myOrders.isEmpty) {
      return const Center(child: Text('No orders to track'));
    }

    final activeOrders = myOrders.where((o) => o['status'] != 'DELIVERED' && o['status'] != 'CANCELLED').toList();
    if (activeOrders.isEmpty) {
      return const Center(child: Text('No active orders to track'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: activeOrders.length,
      itemBuilder: (context, i) {
        final order = activeOrders[i];
        return _buildTrackingCard(order);
      },
    );
  }

  Widget _buildTrackingCard(dynamic order) {
    final stages = ['PENDING', 'ASSIGNED', 'PICKED', 'IN_PROCESS', 'DELIVERED'];
    final currentStage = stages.indexOf(order['status'] ?? 'PENDING');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Order #${order['id']} Progress', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: List.generate(
                stages.length,
                (i) => Column(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: i <= currentStage ? Colors.green : Colors.grey.shade300,
                      ),
                      child: Center(
                        child: Icon(
                          i == 4 ? Icons.check_circle : Icons.circle,
                          color: i <= currentStage ? Colors.white : Colors.grey,
                          size: 20,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      stages[i],
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: i <= currentStage ? FontWeight.bold : FontWeight.normal,
                        color: i <= currentStage ? Colors.green : Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (order['driver'] != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.person, color: Colors.blue),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Driver', style: TextStyle(fontSize: 11, color: Colors.grey)),
                        Text(
                          order['driver']['username'] ?? 'Assigned',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertsTab() {
    if (notifications.isEmpty) {
      return const Center(child: Text('No notifications'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: notifications.length,
      itemBuilder: (context, i) {
        final notif = notifications[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Icon(
              notif['is_read'] ? Icons.mail_outline : Icons.mail,
              color: notif['is_read'] ? Colors.grey : Colors.blue,
            ),
            title: Text(
              notif['message'] ?? 'Notification',
              style: TextStyle(
                fontWeight: notif['is_read'] ? FontWeight.normal : FontWeight.bold,
              ),
            ),
            subtitle: Text(
              notif['created_at']?.toString().split('T')[0] ?? '',
              style: const TextStyle(fontSize: 11),
            ),
            trailing: notif['is_read']
                ? null
                : Container(
                    width: 12,
                    height: 12,
                    decoration: const BoxDecoration(
                      color: Colors.blue,
                      shape: BoxShape.circle,
                    ),
                  ),
          ),
        );
      },
    );
  }

  Widget _buildProfileTab() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: ListView(
        children: [
          // Profile Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 40,
                        backgroundColor: Colors.blue.shade600,
                        child: const Icon(Icons.person, size: 40, color: Colors.white),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text('Customer Profile', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            SizedBox(height: 4),
                            Text('Manage your account settings', style: TextStyle(fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Quick Stats
          Text('Quick Stats', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.grey.shade700)),
          const SizedBox(height: 12),
          ListTile(
            leading: const Icon(Icons.shopping_bag, color: Colors.blue),
            title: const Text('Total Orders'),
            trailing: Text('$totalOrders', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
          ),
          ListTile(
            leading: const Icon(Icons.local_shipping, color: Colors.orange),
            title: const Text('In Transit'),
            trailing: Text('$pendingOrders', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
          ),
          ListTile(
            leading: const Icon(Icons.star, color: Colors.amber),
            title: const Text('Loyalty Points'),
            trailing: Text('$loyaltyPoints', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.amber)),
          ),
          const SizedBox(height: 20),

          // Account Settings
          Text('Account Settings', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.grey.shade700)),
          const SizedBox(height: 12),
          ListTile(
            leading: const Icon(Icons.person_outline),
            title: const Text('Edit Profile'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Profile editing coming soon')),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.location_on_outlined),
            title: const Text('Delivery Address'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Address management coming soon')),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.lock_outline),
            title: const Text('Change Password'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Password change coming soon')),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              minimumSize: const Size.fromHeight(44),
            ),
            onPressed: () {
              context.read<AppState>().logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
            child: const Text('Logout', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _showOrderDetails(dynamic order) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Order #${order['id']}'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _detailRow('Status', order['status']),
              _detailRow('Amount', '₹${order['total_amount']}'),
              _detailRow('Clothes', '${order['clothes_count']} items'),
              _detailRow('Date', order['order_date']?.toString().split('T')[0]),
              if (order['qr_code'] != null) _detailRow('QR Code', order['qr_code']),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
        ],
      ),
    );
  }

  Widget _detailRow(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          Text(value ?? 'N/A', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
        ],
      ),
    );
  }

  void _trackOrder(int orderId) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Tracking order #$orderId...')),
    );
    _tabController.animateTo(1); // Go to tracking tab
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
