import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from orders.models import DriverLocation, Order
from tracking.models import GeofenceEvent
from django.conf import settings
from geopy.distance import geodesic


class LocationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time driver location updates"""
    
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f'location_{self.order_id}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return
        
        # Check for geofence and broadcast
        await self.handle_location_update(latitude, longitude)
    
    async def location_update(self, event):
        """Send location to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'location',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'timestamp': event['timestamp'],
            'accuracy': event.get('accuracy'),
        }))
    
    async def geofence_event(self, event):
        """Send geofence event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'geofence',
            'event': event['event_type'],
            'zone': event['zone_type'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def handle_location_update(self, latitude, longitude):
        """Check geofence and broadcast location"""
        try:
            order = Order.objects.get(id=self.order_id)
            driver = order.driver
            
            # Store location
            location = DriverLocation.objects.create(
                driver=driver,
                order=order,
                latitude=latitude,
                longitude=longitude,
            )
            
            # Check geofence
            self.check_geofence(order, latitude, longitude)
            
            # Broadcast location via async
        except Order.DoesNotExist:
            pass
    
    def check_geofence(self, order, current_lat, current_lng):
        """Check if driver is within geofence zones"""
        radius = settings.GEOFENCE_RADIUS_METERS / 1000  # Convert to km
        
        # Define zones (should come from database in production)
        zones = {
            'PICKUP': (28.6139, 77.2090),  # Example: Delhi
            'DELIVERY': (28.5244, 77.1855),  # Example: Delhi outskirts
        }
        
        current_pos = (float(current_lat), float(current_lng))
        
        for zone_type, zone_coords in zones.items():
            distance = geodesic(current_pos, zone_coords).km
            
            if distance <= radius:
                # Driver entered zone
                GeofenceEvent.objects.create(
                    driver=order.driver,
                    order=order,
                    event_type='ENTERED',
                    zone_type=zone_type,
                    latitude=current_lat,
                    longitude=current_lng,
                )
                
                # Auto-update order status
                if zone_type == 'PICKUP':
                    order.status = 'PICKED'
                    order.save()
                elif zone_type == 'DELIVERY':
                    order.status = 'DELIVERED'
                    order.save()


class OrderUpdatesConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for order status updates"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'orders_{self.user_id}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def order_status_update(self, event):
        """Send order status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': event['order_id'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        }))
    
    async def notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'body': event['body'],
            'timestamp': event['timestamp'],
        }))
