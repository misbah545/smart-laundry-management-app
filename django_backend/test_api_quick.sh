#!/bin/bash
# Quick API Test Script using cURL
# Run this after starting the Django server: python manage.py runserver

echo "╔═══════════════════════════════════════════════╗"
echo "║   Smart Laundry Quick API Tests (cURL)       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

BASE_URL="http://127.0.0.1:8000"

echo "🔹 Testing Login (JWT Authentication)..."
echo "------------------------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"testcustomer","password":"TestPass123!"}')

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*' | sed 's/"access":"//')

if [ -z "$TOKEN" ]; then
    echo ""
    echo "❌ Login failed! Make sure the server is running and test users exist."
    echo "Run: python manage.py runserver"
    exit 1
fi

echo ""
echo "✅ Login successful! Token obtained."
echo ""

echo "🔹 Testing GET All Orders..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/orders/api/orders/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -50

echo ""
echo "🔹 Testing Order Statistics..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/orders/api/orders/statistics/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "🔹 Testing GET All Clothes..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/orders/api/clothes/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo ""
echo "🔹 Testing GET Notifications..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/notifications/api/notifications/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo ""
echo "🔹 Testing GET Unread Notifications..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/notifications/api/notifications/?is_read=false" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo ""
echo "🔹 Testing Complaint Statistics..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/complaints/api/complaints/statistics/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "🔹 Testing GET Feedbacks..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/feedbacks/api/feedbacks/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo ""
echo "🔹 Testing GET AI Predictions..."
echo "------------------------------------------------------"
curl -s -X GET "$BASE_URL/api/ai/api/ai-predictions/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo ""
echo "✅ All API tests completed!"
echo ""
echo "📝 Available Endpoints:"
echo "   - POST /api/login/ - Login & get JWT token"
echo "   - GET  /api/orders/api/orders/ - List orders"
echo "   - GET  /api/orders/api/orders/statistics/ - Order stats"
echo "   - POST /api/orders/api/orders/{id}/update_status/ - Update order status"
echo "   - GET  /api/orders/api/clothes/ - List clothes"
echo "   - GET  /api/notifications/api/notifications/ - List notifications"
echo "   - POST /api/notifications/api/notifications/{id}/mark_as_read/ - Mark as read"
echo "   - GET  /api/feedbacks/api/feedbacks/ - List feedbacks"
echo "   - GET  /api/ai/api/ai-predictions/ - AI predictions"
echo "   - GET  /api/chatbot/api/chatbot-logs/ - Chatbot logs"
echo ""
