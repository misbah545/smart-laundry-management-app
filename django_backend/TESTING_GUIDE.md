# Smart Laundry Backend - Testing & Features Guide

## 🎉 New Features Added

### Enhanced API Endpoints

#### 1. **Order Management**
- ✅ `GET /api/orders/api/orders/` - List all orders with filtering
  - Query params: `customer_id`, `driver_id`, `status`
- ✅ `POST /api/orders/api/orders/{id}/update_status/` - Update order status
- ✅ `GET /api/orders/api/orders/statistics/` - Get order statistics
  - Total orders, revenue, average order value, orders by status
- ✅ `GET /api/orders/api/orders/customer_orders/` - Get current user's orders
- ✅ `GET /api/orders/api/orders/driver_orders/` - Get driver's assigned orders

#### 2. **Cloth Tracking**
- ✅ `GET /api/orders/api/clothes/` - List all clothes with filtering
  - Query params: `order_id`, `status`
- ✅ `POST /api/orders/api/clothes/{id}/update_status/` - Update cloth status

#### 3. **Complaints Management**
- ✅ `GET /api/orders/api/complaints/complaints/` - List complaints
  - Query params: `customer_id`, `status`
- ✅ `POST /api/orders/api/complaints/complaints/{id}/resolve/` - Mark as resolved
- ✅ `GET /api/orders/api/complaints/complaints/statistics/` - Complaint analytics

#### 4. **Notifications**
- ✅ `GET /api/notifications/api/notifications/` - List notifications
  - Query params: `user_id`, `is_read`
- ✅ `POST /api/notifications/api/notifications/{id}/mark_as_read/` - Mark as read
- ✅ `POST /api/notifications/api/notifications/mark_all_read/` - Mark all as read

#### 5. **Feedback System**
- ✅ `GET /api/feedbacks/api/feedbacks/` - List all feedbacks
  - Query params: `customer_id`, `order_id`, `driver_id`

#### 6. **AI & Chatbot**
- ✅ `GET /api/ai/api/ai-predictions/` - AI predictions
- ✅ `GET /api/chatbot/api/chatbot-logs/` - Chatbot conversation logs

---

## 🚀 Quick Start

### 1. **Start the Server**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000`

### 2. **Access Admin Panel**
```
URL: http://127.0.0.1:8000/admin/
Username: admin
Password: admin123
```

### 3. **Test Credentials**
```
Customer: testcustomer / TestPass123!
Driver: testdriver / TestPass123!
```

---

## 🧪 Testing the APIs

### Option 1: Quick cURL Tests (Recommended)
```bash
# Make sure the server is running first!
./test_api_quick.sh
```

### Option 2: Python Test Script
```bash
# In a new terminal (while server is running)
source venv/bin/activate
python test_api.py
```

### Option 3: Manual cURL Tests

#### Login and Get Token
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testcustomer","password":"TestPass123!"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

#### Get Orders
```bash
TOKEN="your_access_token_here"

curl -X GET http://127.0.0.1:8000/api/orders/api/orders/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Order Statistics
```bash
curl -X GET http://127.0.0.1:8000/api/orders/api/orders/statistics/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Update Order Status
```bash
curl -X POST http://127.0.0.1:8000/api/orders/api/orders/1/update_status/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"DELIVERED"}'
```

#### Get Notifications (Unread Only)
```bash
curl -X GET "http://127.0.0.1:8000/api/notifications/api/notifications/?is_read=false" \
  -H "Authorization: Bearer $TOKEN"
```

#### Mark Notification as Read
```bash
curl -X POST http://127.0.0.1:8000/api/notifications/api/notifications/1/mark_as_read/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Sample Data

The database has been populated with:
- **9 Users** (1 admin, 4 customers, 3 drivers)
- **20 Orders** (various statuses)
- **87 Cloth Items** (linked to orders)
- **10 Complaints** (open and resolved)
- **30 Feedbacks** (customer reviews)
- **30 Notifications** (read and unread)
- **15 AI Predictions**
- **25 Chatbot Logs**

---

## 🔍 Advanced Filtering Examples

### Get Orders by Status
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/api/orders/?status=PENDING" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Orders by Customer
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/api/orders/?customer_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Clothes by Order
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/api/clothes/?order_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Open Complaints
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/api/complaints/complaints/?status=OPEN" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📁 Project Structure

```
SmartLaundry/
├── accounts/           # User authentication & profiles
├── orders/            # Order & cloth management
├── complaints/        # Complaints & feedback
├── feedback/          # Feedback system
├── notifications/     # Notification system
├── ai_predictions/    # AI predictions
├── services/          # Chatbot services
├── payments/          # Payment processing
├── backend/           # Django settings & URLs
├── create_sample_data.py    # Sample data generator
├── test_api.py              # Python API test suite
└── test_api_quick.sh        # Quick cURL tests
```

---

## 🔧 Useful Commands

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Clear all data and recreate
python manage.py flush
python create_sample_data.py
```

### Development
```bash
# Start server
python manage.py runserver

# Run in background on specific port
python manage.py runserver 0.0.0.0:8080 &

# Check for errors
python manage.py check
```

---

## 🎯 Next Steps

1. **Frontend Development**: Build React/Vue mobile app to consume APIs
2. **Real-time Features**: Add WebSocket support for live tracking
3. **Payment Integration**: Implement Stripe/Razorpay
4. **Image Upload**: Add support for pickup/delivery proof images
5. **Push Notifications**: Integrate FCM for mobile notifications
6. **Analytics Dashboard**: Build admin analytics with charts
7. **Testing**: Write unit tests and integration tests

---

## 📞 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login/` | Login & get JWT token |
| POST | `/api/refresh/` | Refresh JWT token |
| GET | `/api/orders/api/orders/` | List orders |
| GET | `/api/orders/api/orders/statistics/` | Order statistics |
| POST | `/api/orders/api/orders/{id}/update_status/` | Update order |
| GET | `/api/orders/api/clothes/` | List clothes |
| POST | `/api/orders/api/clothes/{id}/update_status/` | Update cloth |
| GET | `/api/notifications/api/notifications/` | List notifications |
| POST | `/api/notifications/api/notifications/{id}/mark_as_read/` | Mark read |
| GET | `/api/feedbacks/api/feedbacks/` | List feedbacks |
| GET | `/api/ai/api/ai-predictions/` | AI predictions |
| GET | `/api/chatbot/api/chatbot-logs/` | Chatbot logs |

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check for port conflicts
lsof -i :8000

# Kill existing process
pkill -f runserver
```

### Migration errors
```bash
# Reset migrations (WARNING: deletes data)
python manage.py migrate --fake-zero
python manage.py migrate
```

### Token errors
```bash
# Verify token in response
echo "YOUR_TOKEN" | cut -d. -f2 | base64 -d
```

---

**Happy Testing! 🚀**
