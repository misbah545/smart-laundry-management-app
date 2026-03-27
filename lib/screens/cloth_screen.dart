import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/app_state.dart';
import '../widgets/primary_button.dart';

class ClothScreen extends StatefulWidget {
  const ClothScreen({super.key});

  @override
  State<ClothScreen> createState() => _ClothScreenState();
}

class _ClothScreenState extends State<ClothScreen> {
  File? _image;
  bool _loading = false;
  Map<String, dynamic>? _result;

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;
    setState(() => _image = File(picked.path));
  }

  Future<void> _recognize() async {
    if (_image == null) return;
    setState(() => _loading = true);

    final appState = context.read<AppState>();
    final api = ApiClient(baseUrl: appState.baseUrl, token: appState.token);
    final res = await api.recognizeCloth(_image!);

    setState(() {
      _result = res;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text(
          'AI Cloth Recognition',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                if (_image != null)
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.file(_image!, height: 180, fit: BoxFit.cover),
                  )
                else
                  Container(
                    height: 180,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Center(child: Text('Select cloth image')),
                  ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _pickImage,
                        icon: const Icon(Icons.image),
                        label: const Text('Pick Image'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: PrimaryButton(
                        label: 'Recognize',
                        onPressed: _recognize,
                        loading: _loading,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (_result != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Result', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('Cloth Type: ${_result!['cloth_type'] ?? 'N/A'}'),
                  Text('Fabric: ${_result!['fabric'] ?? 'N/A'}'),
                  Text('Color: ${_result!['color'] ?? 'N/A'}'),
                  Text('Confidence: ${_result!['confidence_score'] ?? _result!['confidence'] ?? 'N/A'}'),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
