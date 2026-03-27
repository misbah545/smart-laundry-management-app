from django.db import models
from accounts.models import User
from orders.models import Order


class TrackingAnalytics(models.Model):
    """Analytics for order tracking and driver performance"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='analytics')
    
    # Timing metrics
    time_to_pickup = models.DurationField(null=True, blank=True)  # Time from assignment to pickup
    time_to_delivery = models.DurationField(null=True, blank=True)  # Time from pickup to delivery
    
    # Distance metrics
    distance_traveled = models.FloatField(default=0)  # kilometers
    optimal_distance = models.FloatField(default=0)  # kilometers
    efficiency_score = models.FloatField(default=0)  # 0-100 (distance traveled / optimal)
    
    # Driver performance
    on_time = models.BooleanField(default=False)
    rating = models.FloatField(null=True, blank=True)  # 1-5
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order'], name='tracking_analytics_order_idx'),
            models.Index(fields=['-created_at'], name='tracking_analytics_recent_idx'),
        ]
    
    def __str__(self):
        return f"Analytics for Order {self.order.id}"


class GeofenceEvent(models.Model):
    """Track when driver enters/exits geofenced zones"""
    EVENT_CHOICES = (
        ('ENTERED', 'Entered'),
        ('EXITED', 'Exited'),
    )
    
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='geofence_events')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='geofence_events')
    
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)
    zone_type = models.CharField(max_length=20, choices=[
        ('PICKUP', 'Pickup Zone'),
        ('DELIVERY', 'Delivery Zone'),
    ])
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['driver'], name='geofence_driver_idx'),
            models.Index(fields=['order'], name='geofence_order_idx'),
            models.Index(fields=['event_type'], name='geofence_event_idx'),
            models.Index(fields=['zone_type'], name='geofence_zone_idx'),
            models.Index(fields=['driver', '-timestamp'], name='geofence_driver_recent_idx'),
        ]
    
    def __str__(self):
        return f"{self.event_type} {self.zone_type} by {self.driver.username}"


class AnalyticsSnapshot(models.Model):
    """Aggregated analytics over time"""
    date = models.DateField(unique=True)
    
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    on_time_orders = models.IntegerField(default=0)
    
    avg_delivery_time = models.FloatField(default=0)  # minutes
    avg_distance = models.FloatField(default=0)  # km
    avg_rating = models.FloatField(default=0)  # 1-5
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['date'], name='analytics_snapshot_date_idx'),
            models.Index(fields=['-created_at'], name='analytics_snapshot_recent_idx'),
        ]
    
    def __str__(self):
        return f"Analytics for {self.date}"
