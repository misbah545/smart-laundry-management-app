# Quick Test Guide - SmartLaundry Advanced Features

**Total Setup Time:** ~5 minutes | **Testing Time:** ~15 minutes

---

## 🚀 Start the System (3 Terminals)

### Terminal 1: Redis
```bash
redis-server
# Wait for: "Ready to accept connections on port 6379"
```

### Terminal 2: Django Backend
```bash
cd /home/root123/SmartLaundry
/home/root123/SmartLaundry/venv/bin/daphne -b 0.0.0.0 -p 8000 backend.asgi:application
# Wait for: "Listening on TCP address" and "HTTP/2 support enabled"
```

### Terminal 3: React Native Frontend
```bash
cd /home/root123/SmartLaundry/frontend/smart_laundry_mobile_react
npm start
# Scan QR code with Expo Go app on your phone
```

---

## ✅ Verification Checklist

### System Health
- [ ] Terminal 1: Redis running on port 6379
- [ ] Terminal 2: Daphne listening on port 8000
- [ ] Terminal 3: Expo showing "Metro bundler ready"
- [ ] Frontend app loads without errors

### Feature 1: Chat Messaging
1. Open app → Navigate to "Chat" screen (from order details)
2. Send message: "Hello from customer!"
3. **Expected:** Message appears immediately with timestamp
4. Check backend logs: Should show `Message created` message
5. ✅ **Success:** Message persisted in database

### Feature 2: Photo Upload
1. Open app → Navigate to "Proof Upload" screen
2. Tap "Select Image" → Choose from Camera or Gallery
3. Select any image → Preview shows
4. Tap "Upload" → Loading indicator appears
5. **Expected:** Upload completes, image URL returned
6. Check `/media/proofs/` directory:
   ```bash
   ls -la /home/root123/SmartLaundry/media/proofs/
   ```
7. ✅ **Success:** Photo file exists in media directory

### Feature 3: Analytics Dashboard
1. Open app → Navigate to "Analytics" screen
2. **Verify these elements load:**
   - [ ] KPI cards: "Total Orders", "Completion %", "On-Time %", "Avg Rating"
   - [ ] LineChart: "Delivery Time Trend" (blue line)
   - [ ] LineChart: "Rating Trend" (orange/red line)
   - [ ] PieChart: Status distribution showing colors
   - [ ] Metrics summary below charts
3. No console errors or blank charts
4. ✅ **Success:** Dashboard fully renders with data

### Feature 4: WebSocket Real-Time
1. Terminal 2 backend must show WebSocket connection:
   ```
   WebSocket CONNECT /ws/chat/...
   WebSocket RECEIVE {message data}
   WebSocket SEND broadcast
   ```
2. Open Chat → Send message → Should appear in <1 second
3. ✅ **Success:** WebSocket events logged

### Feature 5: Geofencing
1. Backend must have location tracking enabled
2. Check database for geofence events:
   ```bash
   /home/root123/SmartLaundry/venv/bin/python manage.py dbshell
   SELECT * FROM tracking_geofenceevent LIMIT 5;
   ```
3. If driver moved: Should see ENTERED/EXITED events
4. Check order status: Should show PICKED/DELIVERED
5. ✅ **Success:** GeofenceEvents created in database

### Feature 6: ETA Calculation
1. API endpoint test:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/tracking/analytics/driver_stats/
   ```
2. Response should include:
   ```json
   {
     "average_delivery_time": 23.5,
     "average_distance": 12.4,
     ...
   }
   ```
3. ✅ **Success:** ETA fields returned in API response

---

## 🔧 Troubleshooting

### Issue: "Redis connection refused"
```bash
# Check if Redis is running
redis-cli ping
# If no response, start Redis:
redis-server --daemonize yes
```

### Issue: "Daphne port already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9
# Then restart Daphne
```

### Issue: "Module not found" errors in Django
```bash
# Verify migrations applied
/home/root123/SmartLaundry/venv/bin/python manage.py migrate --check
# If issues, run migrate
/home/root123/SmartLaundry/venv/bin/python manage.py migrate
```

### Issue: "Chart not showing" in Analytics
```bash
# Verify react-native-chart-kit installed
cd /home/root123/SmartLaundry/frontend/smart_laundry_mobile_react
npm list react-native-chart-kit
# If missing: npm install react-native-chart-kit react-native-svg
```

### Issue: "Message not sending"
1. Check Daphne logs for WebSocket errors
2. Verify ChatRoom exists:
   ```bash
   /home/root123/SmartLaundry/venv/bin/python manage.py dbshell
   SELECT * FROM messaging_chatroom;
   ```
3. Try REST endpoint instead of WebSocket:
   ```bash
   curl -X POST http://localhost:8000/api/messaging/messages/send_message/ \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"recipient_id":2,"order_id":1,"content":"test"}'
   ```

---

## 📊 Database Inspection

### View Chat Messages
```bash
cd /home/root123/SmartLaundry
/home/root123/SmartLaundry/venv/bin/python manage.py dbshell
```

Then:
```sql
SELECT * FROM messaging_message ORDER BY created_at DESC LIMIT 5;
SELECT * FROM messaging_chatroom;
```

### View Photo Uploads
```sql
SELECT id, pickup_proof, delivery_proof FROM orders_order 
WHERE pickup_proof != '' OR delivery_proof != '';
```

### View Geofence Events
```sql
SELECT * FROM tracking_geofenceevent ORDER BY timestamp DESC LIMIT 10;
```

### View Analytics
```sql
SELECT * FROM tracking_trackinganalytics ORDER BY created_at DESC LIMIT 5;
```

---

## 🔌 API Testing

### Test Messaging API
```bash
curl -X POST http://localhost:8000/api/messaging/messages/send_message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 2,
    "order_id": 1,
    "content": "Test message"
  }'
```

### Test Analytics API
```bash
curl http://localhost:8000/api/tracking/analytics/driver_stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Photo Upload
```bash
curl -X POST http://localhost:8000/api/orders/1/upload_pickup_proof/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "photo=@/path/to/image.jpg"
```

---

## 📝 Test Scenarios (5 minutes each)

### Scenario A: Customer Messages Driver
**Duration:** 3 minutes

1. Login as customer
2. Open active order
3. Tap "Chat" button
4. Type: "Where are you?"
5. Press Send
6. **Verify:** Message appears with timestamp
7. Check backend: `Message.objects.filter(sender_id=customer_id).count()` increased

### Scenario B: Upload Delivery Proof
**Duration:** 4 minutes

1. Login as driver
2. Open delivered order
3. Tap "Upload Proof"
4. Take photo or select from gallery
5. Confirm upload
6. **Verify:** Photo appears in order details
7. Check filesystem: `ls /home/root123/SmartLaundry/media/proofs/delivery/`

### Scenario C: View Analytics
**Duration:** 2 minutes

1. Login as driver
2. Tap "Analytics" tab
3. Scroll through dashboard
4. **Verify:** All KPI cards show numbers
5. **Verify:** Charts render with data
6. Check console: No errors

---

## 🎯 Success Criteria

**All 6 features working when:**

1. ✅ Chat message sent and received in <1 second
2. ✅ Photo uploaded and stored in /media/proofs/
3. ✅ Analytics dashboard shows KPI cards and charts
4. ✅ Geofence events created in database when location changes
5. ✅ ETA fields returned in API response
6. ✅ WebSocket connections logged in Daphne terminal

**System is production-ready when all criteria met.**

---

## 📞 Quick Commands Reference

```bash
# Start Redis (if not running)
redis-server --daemonize yes

# Start Django Daphne
cd /home/root123/SmartLaundry && /home/root123/SmartLaundry/venv/bin/daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# Start Frontend
cd /home/root123/SmartLaundry/frontend/smart_laundry_mobile_react && npm start

# Check migrations
/home/root123/SmartLaundry/venv/bin/python manage.py migrate --check

# View database
/home/root123/SmartLaundry/venv/bin/python manage.py dbshell

# Check media files
ls -la /home/root123/SmartLaundry/media/

# Test Redis
redis-cli ping
```

---

**Estimated Time to Full Verification:** ~20 minutes

**Expected Outcome:** All 6 features working perfectly with real-time updates

Good luck! 🚀
