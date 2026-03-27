# Smart Laundry API - Complete Endpoint Reference (Updated)

## Authentication

### Login (with Role Info)
```http
POST /api/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user_type": "ADMIN",
  "user_id": 1,
  "username": "admin"
}
```

### Token Refresh
```http
POST /api/refresh/
Content-Type: application/json

{
  "refresh": "eyJ..."
}

Response:
{
  "access": "eyJ..."
}
```

---

## Push Notifications

### Register Device Token
```http
POST /api/notifications/api/notifications/register_token/
Authorization: Bearer <token>
Content-Type: application/json

{
  "token": "ExponentPushToken[xxxxx]",
  "platform": "expo"
}
```

### Send Push Notification (NEW)
```http
POST /api/notifications/api/notifications/send_push/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "title": "Order Updated",
  "body": "Your order #123 is ready",
  "data": {
    "order_id": 123,
    "action": "view_order"
  }
}

Response:
{
  "status": "Push notification sent"
}
```

### List Notifications
```http
GET /api/notifications/api/notifications/
Authorization: Bearer <token>

Query params:
- user_id: int
- is_read: true/false
```

---

## Driver Location Tracking (NEW)

### Update Driver Location
```http
POST /api/orders/api/orders/update_driver_location/
Authorization: Bearer <token>
Content-Type: application/json

{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "order_id": 5
}

Response:
{
  "id": 1,
  "driver": 2,
  "order": 5,
  "latitude": "28.613900",
  "longitude": "77.209000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Get Driver Location for Order
```http
GET /api/orders/api/orders/5/driver_location/
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "driver": 2,
  "order": 5,
  "latitude": "28.613900",
  "longitude": "77.209000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Orders

### List Orders
```http
GET /api/orders/api/orders/
Authorization: Bearer <token>

Query params:
- customer_id: int
- driver_id: int
- status: PENDING/ASSIGNED/PICKED/IN_PROCESS/DELIVERED/CANCELLED
```

### Get Customer's Orders
```http
GET /api/orders/api/orders/customer_orders/
Authorization: Bearer <token>
```

### Get Driver's Orders
```http
GET /api/orders/api/orders/driver_orders/
Authorization: Bearer <token>
```

### Update Order Status (with Auto Push Notification)
```http
POST /api/orders/api/orders/5/update_status/
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "PICKED"
}

Response:
{
  "status": "Order status updated",
  "new_status": "PICKED"
}

Note: Automatically sends push notification to customer
```

### Get Order Statistics
```http
GET /api/orders/api/orders/statistics/
Authorization: Bearer <token>

Response:
{
  "total_orders": 150,
  "by_status": [
    {"status": "PENDING", "count": 10},
    {"status": "DELIVERED", "count": 120}
  ],
  "total_revenue": 45000.00,
  "average_order_value": 300.00
}
```

---

## Payments & Invoices

### Create Payment Intent
```http
POST /api/invoices/create-intent/
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 5,
  "currency": "inr",
  "payment_method_id": "pm_xxxxx"  // Optional, for saved cards
}
```

### Create Stripe Customer
```http
POST /api/invoices/stripe/customer/
Authorization: Bearer <token>
```

### Create Setup Intent (for saving cards)
```http
POST /api/invoices/stripe/setup-intent/
Authorization: Bearer <token>
```

### List Payment Methods (Saved Cards)
```http
GET /api/invoices/stripe/payment-methods/
Authorization: Bearer <token>
```

### Detach Payment Method
```http
POST /api/invoices/stripe/detach/
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_method_id": "pm_xxxxx"
}
```

### Refund Payment
```http
POST /api/invoices/refund/
Authorization: Bearer <token>
Content-Type: application/json

{
  "invoice_id": 10,
  "amount": 500.00,
  "reason": "Customer request"
}
```

### List Invoices
```http
GET /api/invoices/api/invoices/
Authorization: Bearer <token>

Query params:
- customer_id: int
- order_id: int
- payment_status: PENDING/COMPLETED/FAILED/REFUNDED
```

---

## AI/ML Features

### Cloth Recognition
```http
POST /api/chatbot/api/ai/cloth-recognition/
Authorization: Bearer <token>
Content-Type: multipart/form-data

image: <file>
```

### Estimate Price
```http
POST /api/chatbot/api/ai/estimate-price/
Authorization: Bearer <token>
Content-Type: application/json

{
  "clothType": "Shirt",
  "serviceType": "Wash & Iron",
  "quantity": 5
}
```

### Predict Workload
```http
GET /api/chatbot/api/ai/predict-workload/
Authorization: Bearer <token>
```

---

## Loyalty & QR

### Generate QR Code
```http
POST /api/chatbot/api/qr/generate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 5
}
```

### Add Loyalty Points
```http
POST /api/chatbot/api/loyalty/add-points/
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 5
}
```

### Redeem Loyalty Points
```http
POST /api/chatbot/api/loyalty/redeem-points/
Authorization: Bearer <token>
Content-Type: application/json

{
  "points": 100
}
```

---

## Inventory

### Check Inventory
```http
GET /api/chatbot/api/inventory/check/
Authorization: Bearer <token>
```

---

## Complaints & Feedback

### List Complaints
```http
GET /api/complaints/api/complaints/
Authorization: Bearer <token>
```

### Create Complaint
```http
POST /api/complaints/api/complaints/
Authorization: Bearer <token>
Content-Type: application/json

{
  "order": 5,
  "description": "Item damaged",
  "status": "OPEN"
}
```

### Resolve Complaint
```http
POST /api/complaints/api/complaints/3/resolve/
Authorization: Bearer <token>
```

### Get Complaint Statistics
```http
GET /api/complaints/api/complaints/statistics/
Authorization: Bearer <token>
```

### List Feedbacks
```http
GET /api/complaints/api/feedbacks/
Authorization: Bearer <token>
```

### Create Feedback
```http
POST /api/complaints/api/feedbacks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "order": 5,
  "customer": 1,
  "rating": 5,
  "comment": "Great service!"
}
```

---

## OTP Authentication

### Send OTP
```http
POST /api/chatbot/api/auth/send-otp/
Content-Type: application/json

{
  "phone": "+919876543210"
}
```

### Verify OTP
```http
POST /api/chatbot/api/auth/verify-otp/
Content-Type: application/json

{
  "phone": "+919876543210",
  "otp": "123456"
}
```

---

## User Roles

The API uses JWT tokens with embedded `user_type` claim:
- **ADMIN**: Full access to all endpoints
- **CUSTOMER**: Access to own orders, payments, AI features
- **DRIVER**: Access to assigned orders, location updates

Token payload includes:
```json
{
  "user_id": 1,
  "user_type": "ADMIN",
  "username": "admin",
  "email": "admin@example.com",
  "exp": 1234567890
}
```

---

## Webhooks

### Stripe Webhook
```http
POST /api/invoices/stripe/webhook/
Stripe-Signature: <signature>

Handles events:
- payment_intent.succeeded
- payment_intent.payment_failed
- payment_intent.canceled
```

---

## Error Responses

All endpoints return standard error format:

```json
{
  "error": "Error message",
  "detail": "More details if available"
}
```

Status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error

---

## Rate Limiting

Currently no rate limiting implemented. Recommended for production:
- Authentication endpoints: 5 req/min
- Location updates: 60 req/min
- Push notifications: 10 req/min

---

## WebSocket Support

Not yet implemented. Future feature for real-time updates:
- Order status changes
- Driver location updates
- Chat support

---

Last Updated: 2024-01-15
Version: 2.0 (with Push Notifications, Driver Tracking, and Role-Based Access)
