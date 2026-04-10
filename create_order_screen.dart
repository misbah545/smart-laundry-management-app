import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';
import '../utils/validators.dart';

class CreateOrderScreen extends StatefulWidget {
  const CreateOrderScreen({super.key});

  @override
  State<CreateOrderScreen> createState() => _CreateOrderScreenState();
}

class _CreateOrderScreenState extends State<CreateOrderScreen> {
  final _formKey = GlobalKey<FormState>();
  final _clothTypeController = TextEditingController();
  final _quantityController = TextEditingController();
  final _serviceTypeController = TextEditingController();
  final _notesController = TextEditingController();
  
  bool _loading = false;
  List<Map<String, dynamic>> _items = [];

  @override
  void dispose() {
    _clothTypeController.dispose();
    _quantityController.dispose();
    _serviceTypeController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _addItem() {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _items.add({
          'cloth_type': _clothTypeController.text,
          'quantity': int.parse(_quantityController.text),
          'service_type': _serviceTypeController.text,
          'special_instructions': _notesController.text,
        });
      });
      _clearForm();
    }
  }

  void _clearForm() {
    _clothTypeController.clear();
    _quantityController.clear();
    _serviceTypeController.clear();
    _notesController.clear();
  }

  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
    });
  }

  Future<void> _submitOrder() async {
    if (_items.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please add at least one item')),
      );
      return;
    }

    setState(() => _loading = true);

    try {
      final appState = context.read<AppState>();
      final client = ApiClient(baseUrl: appState.baseUrl, token: appState.token);

      final response = await client.createOrder({
        'items': _items,
      });

      if (!mounted) return;

      if (response.containsKey('error')) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${response['message']}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Order created successfully')),
        );
        Navigator.pop(context);
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create New Order'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Add Items',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    value: _clothTypeController.text.isEmpty ? null : _clothTypeController.text,
                    hint: const Text('Select Cloth Type'),
                    items: const [
                      'SHIRT',
                      'PANTS',
                      'JACKET',
                      'DRESS',
                      'SKIRT',
                      'SWEATER',
                      'COAT',
                      'JEANS',
                    ]
                        .map((type) => DropdownMenuItem(
                              value: type,
                              child: Text(type),
                            ))
                        .toList(),
                    onChanged: (value) {
                      if (value != null) {
                        _clothTypeController.text = value;
                      }
                    },
                    validator: (value) => Validators.validateNotEmpty(value, 'Cloth type'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _quantityController,
                    decoration: const InputDecoration(
                      labelText: 'Quantity',
                      hintText: 'Enter quantity',
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) => Validators.validateQuantity(value),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _serviceTypeController.text.isEmpty ? null : _serviceTypeController.text,
                    hint: const Text('Select Service Type'),
                    items: const ['WASH', 'DRY_CLEAN', 'IRON', 'REPAIR']
                        .map((type) => DropdownMenuItem(
                              value: type,
                              child: Text(type),
                            ))
                        .toList(),
                    onChanged: (value) {
                      if (value != null) {
                        _serviceTypeController.text = value;
                      }
                    },
                    validator: (value) => Validators.validateNotEmpty(value, 'Service type'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _notesController,
                    decoration: const InputDecoration(
                      labelText: 'Special Instructions',
                      hintText: 'Add any special instructions',
                    ),
                    maxLines: 3,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _addItem,
                    child: const Text('Add Item'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            if (_items.isNotEmpty) ...[
              const Text(
                'Items in Order',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              ..._items.asMap().entries.map((entry) {
                final index = entry.key;
                final item = entry.value;
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    title: Text('${item['cloth_type']} - ${item['service_type']}'),
                    subtitle: Text('Qty: ${item['quantity']}'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete),
                      onPressed: () => _removeItem(index),
                    ),
                  ),
                );
              }),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: _loading ? null : _submitOrder,
                  child: _loading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Submit Order'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
