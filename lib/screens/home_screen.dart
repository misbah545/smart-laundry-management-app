import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import 'cloth_screen.dart';
import 'inventory_screen.dart';
import 'loyalty_screen.dart';
import 'price_screen.dart';
import 'qr_screen.dart';
import 'workload_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0;

  final _screens = const [
    ClothScreen(),
    PriceScreen(),
    QrScreen(),
    LoyaltyScreen(),
    WorkloadScreen(),
    InventoryScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final appState = context.read<AppState>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Laundry'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => appState.logout(),
          )
        ],
      ),
      body: _screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.checkroom), label: 'Cloth'),
          NavigationDestination(icon: Icon(Icons.attach_money), label: 'Price'),
          NavigationDestination(icon: Icon(Icons.qr_code), label: 'QR'),
          NavigationDestination(icon: Icon(Icons.card_giftcard), label: 'Loyalty'),
          NavigationDestination(icon: Icon(Icons.timeline), label: 'Workload'),
          NavigationDestination(icon: Icon(Icons.inventory_2), label: 'Inventory'),
        ],
      ),
    );
  }
}
