import 'package:flutter/material.dart';

class DriverManagementScreen extends StatefulWidget {
  const DriverManagementScreen({super.key});

  @override
  State<DriverManagementScreen> createState() => _DriverManagementScreenState();
}

class _DriverManagementScreenState extends State<DriverManagementScreen> {
  bool _isLoading = false;
  List<dynamic> drivers = [];
  
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _vehicleController = TextEditingController();
  String _selectedAvailability = 'AVAILABLE';

  @override
  void initState() {
    super.initState();
    _loadDrivers();
  }

  Future<void> _loadDrivers() async {
    // TODO: Add API endpoint in backend to get all drivers
    // For now showing mock data structure
    setState(() => _isLoading = true);
    
    await Future.delayed(const Duration(seconds: 1));
    
    // Mock driver data (until backend endpoint is added)
    setState(() {
      drivers = [
        {
          'id': 1,
          'username': 'mike_driver',
          'phone': '9876543210',
          'vehicle_no': 'DL01AB1234',
          'availability': 'AVAILABLE',
          'total_orders': 24,
          'rating': 4.8,
        },
        {
          'id': 2,
          'username': 'sarah_driver',
          'phone': '9876543211',
          'vehicle_no': 'DL02CD5678',
          'availability': 'BUSY',
          'total_orders': 18,
          'rating': 4.6,
        },
        {
          'id': 3,
          'username': 'testdriver',
          'phone': '9876543212',
          'vehicle_no': 'DL03EF9999',
          'availability': 'OFFLINE',
          'total_orders': 5,
          'rating': 4.9,
        },
      ];
      _isLoading = false;
    });
  }

  void _showAddDriverDialog() {
    _nameController.clear();
    _phoneController.clear();
    _vehicleController.clear();
    _selectedAvailability = 'AVAILABLE';
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add New Driver'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Driver Name', hintText: 'e.g., John Doe'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _phoneController,
                decoration: const InputDecoration(labelText: 'Phone Number', hintText: '9876543210'),
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _vehicleController,
                decoration: const InputDecoration(labelText: 'Vehicle Number', hintText: 'DL01AB1234'),
              ),
              const SizedBox(height: 12),
              DropdownButton<String>(
                value: _selectedAvailability,
                isExpanded: true,
                items: ['AVAILABLE', 'BUSY', 'OFFLINE'].map((status) {
                  return DropdownMenuItem(value: status, child: Text(status));
                }).toList(),
                onChanged: (value) {
                  setState(() => _selectedAvailability = value ?? 'AVAILABLE');
                  Navigator.pop(context);
                  _showAddDriverDialog();
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              // TODO: Add API call to create driver in backend
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('✅ Driver added successfully')),
              );
              Navigator.pop(context);
              _loadDrivers();
            },
            child: const Text('Add Driver'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('👨‍💼 Driver Management'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.indigo.shade700,
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddDriverDialog,
        label: const Text('Add Driver'),
        icon: const Icon(Icons.person_add),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : drivers.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.people_outline, size: 64, color: Colors.grey.shade300),
                      const SizedBox(height: 16),
                      const Text('No drivers yet', style: TextStyle(fontSize: 16, color: Colors.grey)),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _showAddDriverDialog,
                        icon: const Icon(Icons.person_add),
                        label: const Text('Add First Driver'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: drivers.length,
                  itemBuilder: (context, index) {
                    final driver = drivers[index];
                    return _buildDriverCard(driver);
                  },
                ),
    );
  }

  Widget _buildDriverCard(dynamic driver) {
    final availability = driver['availability'] ?? 'OFFLINE';
    final statusColor = availability == 'AVAILABLE'
        ? Colors.green
        : availability == 'BUSY'
            ? Colors.orange
            : Colors.red;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
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
                        driver['username'] ?? 'Unknown',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '📱 ${driver['phone'] ?? 'N/A'}',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    availability,
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Vehicle', style: TextStyle(fontSize: 10, color: Colors.grey)),
                    Text(
                      driver['vehicle_no'] ?? 'N/A',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Orders', style: TextStyle(fontSize: 10, color: Colors.grey)),
                    Text(
                      '${driver['total_orders'] ?? 0}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Rating', style: TextStyle(fontSize: 10, color: Colors.grey)),
                    Row(
                      children: [
                        const Icon(Icons.star, size: 14, color: Colors.amber),
                        const SizedBox(width: 4),
                        Text(
                          '${driver['rating'] ?? 0}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: () {
                    // TODO: Edit driver
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Edit feature coming soon')),
                    );
                  },
                  icon: const Icon(Icons.edit, size: 16),
                  label: const Text('Edit'),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  onPressed: () {
                    // TODO: Delete driver with confirmation
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Delete Driver?'),
                        content: const Text('This action cannot be undone.'),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                          ElevatedButton(
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                            onPressed: () {
                              // TODO: API call to delete
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('✅ Driver deleted')),
                              );
                            },
                            child: const Text('Delete'),
                          ),
                        ],
                      ),
                    );
                  },
                  icon: const Icon(Icons.delete, size: 16, color: Colors.red),
                  label: const Text('Delete'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _vehicleController.dispose();
    super.dispose();
  }
}
