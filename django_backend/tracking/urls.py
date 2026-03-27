from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracking.views import TrackingAnalyticsViewSet, GeofenceEventViewSet, AnalyticsSnapshotViewSet

router = DefaultRouter()
router.register(r'analytics', TrackingAnalyticsViewSet)
router.register(r'geofence-events', GeofenceEventViewSet)
router.register(r'snapshots', AnalyticsSnapshotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
