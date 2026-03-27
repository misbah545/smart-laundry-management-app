# Backend Push Notifications, Live Driver Tracking & Role-Based Navigation - Implementation Summary

## Completed Features

### 1. Backend Push Notification Sending via Expo Push API

**Backend Changes:**

- **Installed Package:** `exponent-server-sdk` for sending Expo push notifications
  
- **notifications/views.py:**
  - Added `send_push_notification(user, title, body, data)` helper function
  - Implements Expo Push API client
  - Handles invalid token removal (DeviceNotRegistered errors)
  - Added `send_push` endpoint (`POST /api/notifications/api/notifications/send_push/`)
    - Accepts: `user_id`, `title`, `body`, `data`
    - Sends push via Expo Push Service
    - Saves notification to database
  
- **orders/views.py:**
  - Updated `update_status` endpoint to auto-send push notifications
  - When order status changes, customer receives push notification
  - Notification includes order ID and status change details

**How It Works:**
1. User registers device token via PushNotificationsScreen
2. Token stored in DeviceToken table
3. When order status updates, backend calls `send_push_notification`
4. Expo Push Service delivers notification to device
5. Invalid tokens automatically removed from database

---

### 2. Live Driver Tracking

**Backend Changes:**

- **orders/models.py:**
  - Created `DriverLocation` model:
    - Fields: `driver`, `order`, `latitude`, `longitude`, `timestamp`
    - Indexed on driver and order for fast queries
    - Auto-updates timestamp on each save

- **orders/serializers.py:**
  - Added `DriverLocationSerializer`

- **orders/views.py:**
  - Added `update_driver_location` endpoint (`POST /api/orders/api/orders/update_driver_location/`)
    - Accepts: `latitude`, `longitude`, `order_id` (optional)
    - Creates location record for driver
  - Added `driver_location` endpoint (`GET /api/orders/api/orders/{order_id}/driver_location/`)
    - Returns latest driver location for order
    - Falls back to driver's most recent location if no order-specific location

- **Database Migration:**
  - Created and applied migration `orders/migrations/0003_driverlocation.py`

**Frontend Changes:**

- **src/api/client.js:**
  - Added `updateDriverLocation(latitude, longitude, orderId)`
  - Added `getDriverLocation(orderId)`

- **src/screens/DriverLocationScreen.js:** (New)
  - Driver-only screen for location sharing
  - Auto-tracking mode (updates every 10 seconds)
  - Manual update button
  - Shows current GPS coordinates and accuracy
  - Requires location permissions
  - Sends location to backend with active order ID

- **src/screens/OrderMapScreen.js:** (Updated)
  - Now shows live driver location
  - Polls for updates every 5 seconds
  - Auto-centers map on driver position
  - Displays "Follow Driver" button
  - Shows last update timestamp
  - Loads active orders (ASSIGNED, PICKED, IN_PROCESS)

- **Package Installed:** `expo-location` for GPS access

**How It Works:**
1. Driver opens DriverLocationScreen
2. Driver enables auto-tracking
3. App sends GPS coordinates every 10 seconds to backend
4. Backend stores location in DriverLocation table
5. Customer opens OrderMapScreen
6. Map polls backend every 5 seconds for driver location
7. Map updates green marker showing driver position
8. Customer can follow driver in real-time

---

### 3. Role-Based Admin/Customer/Driver Tabs

**Backend Changes:**

- **accounts/serializers.py:**
  - Created `CustomTokenObtainPairSerializer`
  - Adds `user_type`, `username`, `email` to JWT token claims
  - Returns `user_type`, `username`, `user_id` in login response

- **backend/urls.py:**
  - Created `CustomTokenObtainPairView` using custom serializer
  - Updated `/api/login/` to use custom view

**Frontend Changes:**

- **src/context/AuthContext.js:** (Updated)
  - Added state: `userType`, `userId`, `username`
  - Updated `login()` to accept and store user data
  - Persists user data to AsyncStorage
  - Exposes user data to components

- **src/screens/LoginScreen.js:** (Updated)
  - Extracts `user_type`, `user_id`, `username` from login response
  - Passes user data to `login()` function

- **App.js:** (Updated)
  - Implements role-based tab filtering
  - Defines separate screen sets for ADMIN, CUSTOMER, DRIVER
  - Dynamically renders tabs based on `userType`

**Role-Specific Screens:**

**ADMIN:**
- Admin Dashboard, Orders, Status, Map, Payment, Refunds, Support, Push Notifications
- All AI/ML features: Cloth Recognition, Price Estimation, QR, Loyalty, Workload, Inventory

**CUSTOMER:**
- Orders, Map, Payment, Cards, History
- AI features: Cloth, Price, QR, Loyalty
- Support

**DRIVER:**
- MyOrders, Status, Location (GPS tracking), Map, Support

**How It Works:**
1. User logs in with username/password
2. Backend returns JWT token with `user_type` claim
3. Frontend stores `user_type` in AsyncStorage
4. App.js reads `userType` from AuthContext
5. Tabs component renders role-appropriate screens
6. Each user sees only relevant features

---

## API Endpoints Added

### Push Notifications
- `POST /api/notifications/api/notifications/send_push/`
  - Body: `{user_id, title, body, data}`
  - Sends push notification via Expo Push Service

### Driver Location
- `POST /api/orders/api/orders/update_driver_location/`
  - Body: `{latitude, longitude, order_id?}`
  - Updates driver GPS location

- `GET /api/orders/api/orders/{order_id}/driver_location/`
  - Returns latest driver location for order

---

## Database Models Added

### DriverLocation
```python
class DriverLocation(models.Model):
    driver = ForeignKey(User)
    order = ForeignKey(Order, null=True)
    latitude = DecimalField(max_digits=9, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    timestamp = DateTimeField(auto_now=True)
```

---

## Mobile App Screens

### New Screens Created
1. **DriverLocationScreen.js** - Driver GPS tracking control panel

### Updated Screens
1. **OrderMapScreen.js** - Live driver tracking map with polling
2. **LoginScreen.js** - Stores user role on login
3. **App.js** - Role-based navigation

---

## Testing Instructions

### 1. Test Push Notifications

**Backend:**
```bash
# Start Django server
python manage.py runserver

# Test push send (requires device token registered)
curl -X POST http://localhost:8000/api/notifications/api/notifications/send_push/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "Test", "body": "Hello from backend!"}'
```

**Mobile App:**
1. Open PushNotificationsScreen
2. Tap "Register for Push"
3. Allow notifications permission
4. Update an order status from another device/admin panel
5. You should receive a push notification

### 2. Test Driver Tracking

**Driver Side:**
1. Login as DRIVER user
2. Navigate to "Location" tab
3. Enable auto-tracking switch
4. Allow location permission
5. Tap "Update Location Now"

**Customer Side:**
1. Login as CUSTOMER user
2. Navigate to "Map" tab
3. Select active order
4. Green marker shows driver location
5. Tap "Follow Driver" to center map
6. Location updates every 5 seconds

### 3. Test Role-Based Navigation

**ADMIN Login:**
```
Username: admin
Password: admin123
```
- Should see: Admin, Orders, Status, Map, Payment, Refunds, Support, Push, Cloth, Price, QR, Loyalty, Workload, Inventory

**CUSTOMER Login:**
- Should see: Orders, Map, Payment, Cards, History, Cloth, Price, QR, Loyalty, Support

**DRIVER Login:**
- Should see: MyOrders, Status, Location, Map, Support

---

## Configuration

### Backend
- No additional config needed (uses existing Expo Push Service)

### Mobile App
- Ensure `expo-location` is installed: `npm install expo-location`
- Location permissions handled automatically by app

---

## Key Features Summary

✅ **Backend push notification sending** via Expo Push API
✅ **Auto-notifications** on order status changes
✅ **Driver location tracking** with GPS
✅ **Live location updates** every 10 seconds (driver) / 5 seconds polling (customer)
✅ **Real-time map** with driver marker
✅ **Role-based navigation** (ADMIN/CUSTOMER/DRIVER)
✅ **Custom JWT tokens** with user_type claim
✅ **Persistent user role** in AsyncStorage

---

## File Changes Summary

### Backend Files Modified:
- `notifications/views.py` - Added push sending logic
- `orders/models.py` - Added DriverLocation model
- `orders/serializers.py` - Added DriverLocationSerializer
- `orders/views.py` - Added location endpoints, auto-notifications
- `orders/admin.py` - Registered DriverLocation
- `accounts/serializers.py` - Custom JWT serializer
- `backend/urls.py` - Custom login view
- `requirements.txt` - Added exponent-server-sdk

### Frontend Files Modified:
- `src/context/AuthContext.js` - User role state management
- `src/screens/LoginScreen.js` - Pass user data on login
- `src/api/client.js` - Added location/push APIs
- `App.js` - Role-based tab rendering

### Frontend Files Created:
- `src/screens/DriverLocationScreen.js` - Driver GPS tracking

### Migrations Created:
- `orders/migrations/0003_driverlocation.py`

---

## Next Steps / Future Enhancements

1. **WebSockets for Real-Time Updates** - Replace polling with WebSocket for instant driver location updates
2. **Route Optimization** - Show driver route on map with polylines
3. **ETA Calculation** - Estimate time to pickup/delivery based on distance
4. **Geofencing** - Auto-update order status when driver reaches destination
5. **Push Notification Preferences** - Allow users to customize notification settings
6. **Offline Support** - Cache location updates when offline, sync when online
7. **Battery Optimization** - Reduce location update frequency when driver is idle

---

## Architecture Notes

- **Push Notifications:** Expo Push Service (cloud-based, no Firebase needed)
- **Location Storage:** PostgreSQL with indexed queries
- **Real-Time Updates:** HTTP polling (5-10 second intervals)
- **Authentication:** JWT with custom claims
- **Authorization:** Role-based tab filtering (frontend), can add backend permissions

---

All features are now fully implemented and ready for testing!
