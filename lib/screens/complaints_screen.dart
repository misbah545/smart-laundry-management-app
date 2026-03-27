import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../core/api_client.dart';

class ComplaintsScreen extends StatefulWidget {
  const ComplaintsScreen({super.key});

  @override
  State<ComplaintsScreen> createState() => _ComplaintsScreenState();
}

class _ComplaintsScreenState extends State<ComplaintsScreen> {
  List<dynamic> complaints = [];
  bool _isLoading = true;
  String _selectedStatus = 'OPEN';

  @override
  void initState() {
    super.initState();
    _loadComplaints();
  }

  Future<void> _loadComplaints() async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    
    try {
      final response = await client.getAdminComplaints(_selectedStatus);
      if (mounted) {
        setState(() {
          complaints = response['complaints'] ?? [];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading complaints: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _resolveComplaint(int complaintId) async {
    final appState = context.read<AppState>();
    final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    final controller = TextEditingController();

    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Resolve Complaint'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'Enter resolution message',
            border: OutlineInputBorder(),
          ),
          maxLines: 3,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              try {
                await client.resolveComplaint(complaintId, controller.text);
                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Complaint resolved'), backgroundColor: Colors.green),
                  );
                  _loadComplaints();
                }
              } catch (e) {
                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                  );
                }
              }
            },
            child: const Text('Resolve'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Complaint Resolution', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                const Text('Filter: ', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(width: 8),
                Expanded(
                  child: SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(label: Text('Open'), value: 'OPEN'),
                      ButtonSegment(label: Text('Resolved'), value: 'RESOLVED'),
                    ],
                    selected: {_selectedStatus},
                    onSelectionChanged: (value) {
                      setState(() => _selectedStatus = value.first);
                      _loadComplaints();
                    },
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : complaints.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.check_circle_outline, size: 64, color: Colors.grey.shade400),
                            const SizedBox(height: 16),
                            Text('No $_selectedStatus complaints', style: TextStyle(color: Colors.grey.shade600)),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: complaints.length,
                        itemBuilder: (context, index) {
                          final complaint = complaints[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 8),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: complaint['status'] == 'OPEN' ? Colors.red.shade100 : Colors.green.shade100,
                                child: Icon(
                                  complaint['status'] == 'OPEN' ? Icons.warning : Icons.check,
                                  color: complaint['status'] == 'OPEN' ? Colors.red : Colors.green,
                                ),
                              ),
                              title: Text('${complaint['issue_type'] ?? 'Complaint'} #${complaint['id']}'),
                              subtitle: Text(complaint['description'] ?? ''),
                              trailing: complaint['status'] == 'OPEN'
                                  ? IconButton(
                                      icon: const Icon(Icons.done, color: Colors.green),
                                      onPressed: () => _resolveComplaint(complaint['id']),
                                    )
                                  : const Icon(Icons.check_circle, color: Colors.green),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
