from rest_framework import serializers
from tracking.models import TrackingAnalytics, GeofenceEvent, AnalyticsSnapshot


class TrackingAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingAnalytics
        fields = ['id', 'order', 'time_to_pickup', 'time_to_delivery', 'distance_traveled', 'optimal_distance', 'efficiency_score', 'on_time', 'rating']


class GeofenceEventSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    
    class Meta:
        model = GeofenceEvent
        fields = ['id', 'driver', 'driver_name', 'order', 'event_type', 'zone_type', 'latitude', 'longitude', 'timestamp']


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = ['id', 'date', 'total_orders', 'completed_orders', 'on_time_orders', 'avg_delivery_time', 'avg_distance', 'avg_rating']
