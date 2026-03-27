import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary = Color(0xFF2B6CB0);
  static const Color secondary = Color(0xFF38B2AC);
  static const Color background = Color(0xFFF7FAFC);
  static const Color card = Color(0xFFFFFFFF);

  static ThemeData light() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        secondary: secondary,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: background,
      cardTheme: const CardThemeData(
        elevation: 2,
        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
    );
  }
}
