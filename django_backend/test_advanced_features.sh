#!/bin/bash
# Test script for Advanced Smart Laundry Features

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Smart Laundry - Advanced Features Test Suite             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://127.0.0.1:8000"

# Login first
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*' | sed 's/"access":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Make sure server is running."
    exit 1
fi

echo "✅ Login successful!"
echo ""

# Test 1: Send OTP
echo "📱 Test 1: Send OTP"
echo "------------------------------------------------------"
curl -s -X POST "$BASE_URL/api/chatbot/api/auth/send-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"+1234567890"}' | python3 -m json.tool
echo ""

# Test 2: AI Price Estimation
echo "💰 Test 2: ML Price Estimation"
echo "------------------------------------------------------"
curl -s -X POST "$BASE_URL/api/chatbot/api/ai/estimate-price/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cloth_type":"Shirt","fabric":"SILK","service_type":"DRY_CLEAN","weight":0.5}' | python3 -m json.tool
echo ""

# Test 3: Generate QR Codes
echo "🔲 Test 3: Generate QR Codes"
echo "------------------------------------------------------"
curl -s -X POST "$BASE_URL/api/chatbot/api/qr/generate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id":1}' | python3 -m json.tool
echo ""

# Test 4: Generate Digital Invoice
echo "🧾 Test 4: Generate Digital Invoice"
echo "------------------------------------------------------"
curl -s -X POST "$BASE_URL/api/chatbot/api/invoice/generate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id":1}' | python3 -m json.tool
echo ""

# Test 5: Add Loyalty Points
echo "⭐ Test 5: Add Loyalty Points"
echo "------------------------------------------------------"
curl -s -X POST "$BASE_URL/api/chatbot/api/loyalty/add-points/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id":1}' | python3 -m json.tool
echo ""

# Test 6: AI Workload Prediction
echo "📊 Test 6: AI Workload Prediction"
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/chatbot/api/ai/predict-workload/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -40
echo ""

# Test 7: Check Inventory
echo "📦 Test 7: Check Inventory"
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/chatbot/api/inventory/check/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "✅ All advanced features tested!"
echo ""
echo "📚 For complete API documentation, see:"
echo "   - ADVANCED_FEATURES.md"
echo ""
