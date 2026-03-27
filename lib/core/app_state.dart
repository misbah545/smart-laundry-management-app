import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppState extends ChangeNotifier {
  String? _token;
  String? _username;
  String? _userType;
  int? _userId;
  String _baseUrl = 'http://127.0.0.1:8000';

  String? get token => _token;
  String? get username => _username;
  String? get userType => _userType;
  int? get userId => _userId;
  String get baseUrl => _baseUrl;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;
  bool get isAdmin => _userType == 'ADMIN';

  Future<void> loadFromStorage() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token');
    _username = prefs.getString('username');
    _userType = prefs.getString('userType');
    _userId = prefs.getInt('userId');
    _baseUrl = prefs.getString('baseUrl') ?? _baseUrl;
    notifyListeners();
  }

  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
    notifyListeners();
  }

  Future<void> setSession(String token, String userType, String username, int userId) async {
    _token = token;
    _userType = userType;
    _username = username;
    _userId = userId;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
    await prefs.setString('userType', userType);
    await prefs.setString('username', username);
    await prefs.setInt('userId', userId);
    notifyListeners();
  }

  Future<void> setBaseUrl(String url) async {
    _baseUrl = url.trim().isEmpty ? _baseUrl : url.trim();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('baseUrl', _baseUrl);
    notifyListeners();
  }

  Future<void> logout() async {
    _token = null;
    _username = null;
    _userType = null;
    _userId = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('username');
    await prefs.remove('userType');
    await prefs.remove('userId');
    notifyListeners();
  }
}
