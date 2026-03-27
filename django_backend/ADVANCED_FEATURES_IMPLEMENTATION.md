# Advanced Features Implementation Guide
## WebSockets, Geofencing, Chat, Photo Upload, ETA & Analytics

---

## 1. WebSocket Real-Time Updates

### Architecture

```
Django Channels (ASGI) ← → Redis Channel Layer
       ↓
   WebSocket Consumers
       ↓
   Frontend (React Native)
```

### Setup Complete ✅

**Files Modified:**
- `backend/settings.py` - Added Channels and Redis config
- `backend/asgi.py` - Configured ASGI with WebSocket routing
- `backend/routing.py` - WebSocket URL patterns
- `messaging/consumers.py` - Chat consumer
- `tracking/consumers.py` - Location & order update consumers

### WebSocket Endpoints

**1. Chat WebSocket**
```
ws://localhost:8000/ws/chat/{room_id}/

Messages:
{
  "type": "message",
  "message": "Hello!",
  "sender_id": 1,
  "sender_name": "john",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**2. Live Location WebSocket**
```
ws://localhost:8000/ws/location/{order_id}/

Send:
{
  "latitude": 28.6139,
  "longitude": 77.2090
}

Receive:
{
  "type": "location",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timestamp": "2024-01-15T10:30:00Z"
}

Or (Geofence Event):
{
  "type": "geofence",
  "event": "ENTERED",
  "zone": "PICKUP",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**3. Order Updates WebSocket**
```
ws://localhost:8000/ws/orders/{user_id}/

Receive:
{
  "type": "order_update",
  "order_id": 123,
  "status": "PICKED",
  "timestamp": "2024-01-15T10:30:00Z"
}

Or:
{
  "type": "notification",
  "title": "Order Ready",
  "body": "Your order is ready for pickup",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Running with WebSockets

```bash
# Development: Use Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# Production: Use Gunicorn + Daphne
gunicorn --worker-class daphne.workers.UnicornWorker --workers 4 backend.asgi:application
```

### Redis Setup (Required)

```bash
# Install Redis
brew install redis  # macOS
apt-get install redis-server  # Ubuntu

# Start Redis
redis-server

# Verify
redis-cli ping  # Should return PONG
```

---

## 2. Geofencing & Auto-Status Updates

### How It Works

1. Driver sends GPS coordinates via WebSocket
2. Backend checks if within geofence radius (100m default)
3. Automatically updates order status:
   - Enters **PICKUP** zone → Status = `PICKED`
   - Enters **DELIVERY** zone → Status = `DELIVERED`

### Configuration

**In `backend/settings.py`:**
```python
GEOFENCE_RADIUS_METERS = 100  # Radius for geofence
GEOFENCE_CHECK_INTERVAL = 60  # Check every 60 seconds
```

### Zones (currently hardcoded, should be in DB in production)

```python
zones = {
    'PICKUP': (28.6139, 77.2090),    # Laundry center
    'DELIVERY': (28.5244, 77.1855),  # Delivery hub
}
```

### Geofence Events Stored

```
Model: GeofenceEvent
- driver
- order
- event_type: ENTERED/EXITED
- zone_type: PICKUP/DELIVERY
- latitude, longitude
- timestamp
```

### API: Get Geofence Events for Order

```http
GET /api/tracking/geofence-events/?order_id=5

Response:
[
  {
    "id": 1,
    "driver": 2,
    "driver_name": "john_driver",
    "order": 5,
    "event_type": "ENTERED",
    "zone_type": "PICKUP",
    "latitude": "28.613900",
    "longitude": "77.209000",
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

---

## 3. Chat Messaging System

### Models

```python
Message
- sender (User FK)
- recipient (User FK)
- order (Order FK, nullable)
- content (TextField)
- timestamp (auto)
- is_read (Boolean)

ChatRoom
- participants (M2M User)
- order (OneToOne Order, nullable)
- created_at, updated_at
```

### REST API Endpoints

**Create/Get Chat Room**
```http
POST /api/messaging/rooms/create_room/
{
  "user_id": 2,
  "order_id": 5
}

Response:
{
  "id": 1,
  "room_id": "chat_1",
  "participants": [...],
  "order": 5,
  "messages": [...],
  "last_message": {...},
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Send Message (REST)**
```http
POST /api/messaging/messages/send_message/
{
  "recipient_id": 2,
  "content": "When will you pickup?",
  "order_id": 5
}
```

**Get Conversation with User**
```http
GET /api/messaging/messages/conversation/?user_id=2

Response: [Message objects]
```

**Get All Messages in Room**
```http
GET /api/messaging/rooms/1/messages/
```

**Mark Message as Read**
```http
POST /api/messaging/messages/1/mark_as_read/
```

### WebSocket Chat Example

```javascript
// Connect
const socket = new WebSocket('ws://localhost:8000/ws/chat/chat_1/');

// Send message
socket.send(JSON.stringify({
  message: "Hello!",
  recipient_id: 2
}));

// Receive
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.sender_name}: ${data.message}`);
};
```

---

## 4. Photo Upload for Proof

### Endpoints

**Upload Pickup Proof**
```http
POST /api/orders/5/upload_pickup_proof/
Content-Type: multipart/form-data

image: <file>

Response:
{
  "status": "Pickup proof uploaded"
}
```

**Upload Delivery Proof**
```http
POST /api/orders/5/upload_delivery_proof/
Content-Type: multipart/form-data

image: <file>

Response:
{
  "status": "Delivery proof uploaded"
}

Side Effects:
- Updates order.status = DELIVERED
- Sends push notification to customer
- Records delivery_proof_timestamp
```

### Database Fields

```python
Order model:
- pickup_proof: ImageField(upload_to='proofs/pickup/')
- pickup_proof_timestamp: DateTimeField
- delivery_proof: ImageField(upload_to='proofs/delivery/')
- delivery_proof_timestamp: DateTimeField
```

### File Storage

```
MEDIA_ROOT: /path/to/SmartLaundry/media/
MEDIA_URL: /media/

Uploaded files:
- media/proofs/pickup/{order_id}_pickup.jpg
- media/proofs/delivery/{order_id}_delivery.jpg
```

---

## 5. Route Optimization & ETA Calculation

### Algorithm

Uses **Haversine formula** to calculate distance between coordinates:

```python
from geopy.distance import geodesic

distance_km = geodesic(
    (lat1, lng1),  # Current location
    (lat2, lng2)   # Destination
).kilometers

eta_minutes = (distance_km / avg_speed) * 60
# avg_speed = 25 km/h (typical delivery speed)
```

### ETA Storage

```python
DriverLocation model:
- eta_minutes: IntegerField (estimated time in minutes)
- distance_remaining_km: FloatField (remaining distance)

Updated when driver location changes
```

### API: Get ETA

```http
GET /api/orders/5/driver_location/

Response:
{
  "id": 10,
  "driver": 2,
  "order": 5,
  "latitude": "28.613900",
  "longitude": "77.209000",
  "eta_minutes": 15,
  "distance_remaining_km": 6.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Algorithm Implementation (Frontend)

```javascript
// Calculate ETA
const calculateETA = (distance, avgSpeed = 25) => {
  const etaHours = distance / avgSpeed;
  const etaMinutes = Math.ceil(etaHours * 60);
  return etaMinutes;
};

// Example
const eta = calculateETA(6.2);  // 15 minutes
```

---

## 6. Analytics Dashboard Enhancements

### Models

```python
TrackingAnalytics (per order)
- order (OneToOne)
- time_to_pickup: Duration
- time_to_delivery: Duration
- distance_traveled: Float (km)
- optimal_distance: Float (km)
- efficiency_score: Float (0-100)
- on_time: Boolean
- rating: Float (1-5)

AnalyticsSnapshot (daily aggregated)
- date: DateField (unique)
- total_orders: Int
- completed_orders: Int
- on_time_orders: Int
- avg_delivery_time: Float (minutes)
- avg_distance: Float (km)
- avg_rating: Float (1-5)
```

### API Endpoints

**Get Order Analytics**
```http
GET /api/tracking/analytics/order_analytics/?order_id=5

Response:
{
  "id": 1,
  "order": 5,
  "time_to_pickup": "00:45:30",
  "time_to_delivery": "01:20:15",
  "distance_traveled": 12.5,
  "optimal_distance": 10.2,
  "efficiency_score": 81.6,
  "on_time": true,
  "rating": 4.5
}
```

**Get Driver Performance Stats**
```http
GET /api/tracking/analytics/driver_stats/?driver_id=2&days=30

Response:
{
  "total_orders": 45,
  "completed_orders": 43,
  "on_time": 39,
  "avg_rating": 4.7,
  "avg_efficiency": 85.3,
  "total_distance": 487.5
}
```

**Get Dashboard Data (Aggregated)**
```http
GET /api/tracking/snapshots/dashboard/?days=30

Response:
{
  "total_orders": 1250,
  "completed_orders": 1180,
  "on_time_orders": 980,
  "avg_delivery_time": 45.2,
  "avg_distance": 12.3,
  "avg_rating": 4.6,
  "snapshots": [
    {
      "date": "2024-01-15",
      "total_orders": 42,
      "completed_orders": 40,
      "on_time_orders": 38,
      "avg_delivery_time": 43.5,
      "avg_distance": 12.1,
      "avg_rating": 4.7
    }
  ]
}
```

### Metrics Explained

| Metric | Formula | Example |
|--------|---------|---------|
| **Efficiency Score** | (optimal_distance / distance_traveled) × 100 | 10 km / 12.5 km × 100 = 80% |
| **Delivery Time** | Time from pickup to delivery | 1 hour 20 minutes |
| **On-Time Rate** | (orders_on_time / completed_orders) × 100 | 39 / 43 × 100 = 90.7% |
| **Average Rating** | Sum of all ratings / count | (4.8 + 4.5 + 4.9) / 3 = 4.7 |

---

## 7. Error Handling & Loading States

### Backend Error Responses

All errors follow this format:

```json
{
  "error": "Short error message",
  "detail": "More detailed explanation",
  "status_code": 400
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (missing/invalid params) |
| 401 | Unauthorized (no token) |
| 403 | Forbidden (permission denied) |
| 404 | Not Found |
| 500 | Server Error |

### Common Errors

**Missing Required Field**
```json
{
  "error": "latitude and longitude required",
  "detail": "Both coordinates are needed for location update"
}
```

**No Driver Assigned**
```json
{
  "error": "No driver assigned",
  "detail": "Order must have a driver before location tracking"
}
```

**Geofence Processing**
- Try/catch block handles geopy errors
- Invalid coordinates silently skip geofence check
- No error response (graceful degradation)

---

## 8. Offline Support

### Local Storage Strategy

```javascript
// Store pending actions
const pendingActions = {
  location_updates: [],
  message_sends: [],
  photo_uploads: [],
};

// On reconnect, retry in order
const syncPendingActions = async () => {
  for (const action of pendingActions.location_updates) {
    await api.updateDriverLocation(action);
  }
  // Clear queue
  pendingActions.location_updates = [];
};
```

### IndexedDB for Message Queue

```javascript
import Dexie from 'dexie';

const db = new Dexie('SmartLaundryDB');
db.version(1).stores({
  pending_messages: '++id,recipient_id',
  location_queue: '++id,order_id',
});

// Store when offline
await db.pending_messages.add({
  recipient_id: 2,
  content: "Hello!",
  timestamp: Date.now(),
});

// Sync when online
window.addEventListener('online', async () => {
  const messages = await db.pending_messages.toArray();
  for (const msg of messages) {
    await api.sendMessage(msg);
    await db.pending_messages.delete(msg.id);
  }
});
```

---

## Database Schema Summary

```
Message
  sender_id → User
  recipient_id → User
  order_id → Order (nullable)
  content, timestamp, is_read

ChatRoom
  participant_ids → User (M2M)
  order_id → Order (nullable, unique)

DriverLocation
  driver_id → User
  order_id → Order
  latitude, longitude, timestamp
  eta_minutes, distance_remaining_km

TrackingAnalytics
  order_id → Order (unique)
  timing metrics, distance metrics
  efficiency, on_time, rating

GeofenceEvent
  driver_id → User
  order_id → Order
  event_type, zone_type
  latitude, longitude, timestamp

AnalyticsSnapshot
  date (unique)
  aggregated stats for the day
```

---

## Testing WebSockets

### Using WebSocket-Client (Python)

```python
import websocket
import json
import time

ws = websocket.create_connection("ws://localhost:8000/ws/location/5/")

# Send location
location = {
    "latitude": 28.6139,
    "longitude": 77.2090,
}
ws.send(json.dumps(location))

# Receive updates
while True:
    data = ws.recv()
    print("Received:", json.loads(data))
    time.sleep(1)

ws.close()
```

### Using Browser Console

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/orders/1/');

ws.onopen = () => {
    console.log('Connected');
};

ws.onmessage = (event) => {
    console.log('Received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
    console.error('Error:', error);
};

ws.onclose = () => {
    console.log('Disconnected');
};
```

---

## Deployment Checklist

- [ ] Install and configure Redis
- [ ] Update Django settings for production
- [ ] Use Daphne or asgiref for ASGI
- [ ] Configure WebSocket firewall rules
- [ ] Set up SSL/TLS for WSS (secure WebSocket)
- [ ] Configure channel layer authentication
- [ ] Test geofencing with real coordinates
- [ ] Set up daily analytics snapshot cron job
- [ ] Configure CORS for WebSocket origins
- [ ] Monitor Redis memory usage
- [ ] Set up error logging for consumers

---

## Performance Optimization Tips

1. **Connection Pooling**
   - Use connection pool for Redis
   - Limit max WebSocket connections

2. **Message Filtering**
   - Only send location updates if distance > 10m
   - Throttle to max 1 update per 5 seconds

3. **Database Indexes**
   - Index on (driver, timestamp)
   - Index on (order, timestamp)

4. **Batch Operations**
   - Group analytics snapshots
   - Bulk create geofence events

5. **Cache Frequently Accessed Data**
   - Cache driver stats
   - Cache order details

---

All features are now fully implemented! 🚀
