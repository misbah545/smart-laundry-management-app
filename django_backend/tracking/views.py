from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from tracking.models import TrackingAnalytics, GeofenceEvent, AnalyticsSnapshot
from tracking.serializers import TrackingAnalyticsSerializer, GeofenceEventSerializer, AnalyticsSnapshotSerializer
from orders.models import Order


class TrackingAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = TrackingAnalytics.objects.all()
    serializer_class = TrackingAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def order_analytics(self, request):
        """Get analytics for a specific order"""
        order_id = request.query_params.get('order_id')
        
        if not order_id:
            return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            analytics = TrackingAnalytics.objects.get(order_id=order_id)
            serializer = TrackingAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except TrackingAnalytics.DoesNotExist:
            return Response({'error': 'Analytics not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def driver_stats(self, request):
        """Get driver performance statistics"""
        driver_id = request.query_params.get('driver_id')
        days = int(request.query_params.get('days', 30))
        
        if not driver_id:
            return Response({'error': 'driver_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get orders for driver in last N days
        start_date = timezone.now() - timedelta(days=days)
        orders = Order.objects.filter(
            driver_id=driver_id,
            order_date__gte=start_date
        )
        
        analytics = TrackingAnalytics.objects.filter(order__in=orders)
        
        stats = {
            'total_orders': orders.count(),
            'completed_orders': orders.filter(status='DELIVERED').count(),
            'on_time': analytics.filter(on_time=True).count(),
            'avg_rating': analytics.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0,
            'avg_efficiency': analytics.aggregate(avg_eff=models.Avg('efficiency_score'))['avg_eff'] or 0,
            'total_distance': analytics.aggregate(total=models.Sum('distance_traveled'))['total'] or 0,
        }
        
        return Response(stats)


class GeofenceEventViewSet(viewsets.ModelViewSet):
    queryset = GeofenceEvent.objects.all()
    serializer_class = GeofenceEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def order_events(self, request):
        """Get geofence events for an order"""
        order_id = request.query_params.get('order_id')
        
        if not order_id:
            return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        events = GeofenceEvent.objects.filter(order_id=order_id)
        serializer = GeofenceEventSerializer(events, many=True)
        return Response(serializer.data)


class AnalyticsSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get analytics dashboard data"""
        days = int(request.query_params.get('days', 30))
        
        start_date = timezone.now() - timedelta(days=days)
        snapshots = AnalyticsSnapshot.objects.filter(date__gte=start_date.date())
        
        # Aggregate stats
        stats = {
            'total_orders': snapshots.aggregate(models.Sum('total_orders'))['total_orders__sum'] or 0,
            'completed_orders': snapshots.aggregate(models.Sum('completed_orders'))['completed_orders__sum'] or 0,
            'on_time_orders': snapshots.aggregate(models.Sum('on_time_orders'))['on_time_orders__sum'] or 0,
            'avg_delivery_time': snapshots.aggregate(models.Avg('avg_delivery_time'))['avg_delivery_time__avg'] or 0,
            'avg_distance': snapshots.aggregate(models.Avg('avg_distance'))['avg_distance__avg'] or 0,
            'avg_rating': snapshots.aggregate(models.Avg('avg_rating'))['avg_rating__avg'] or 0,
            'snapshots': AnalyticsSnapshotSerializer(snapshots, many=True).data,
        }
        
        return Response(stats)


# Fix imports
from django.db import models
