from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CustomerProfileViewSet, DriverProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'customers', CustomerProfileViewSet, basename='customerprofile')
router.register(r'drivers', DriverProfileViewSet, basename='driverprofile')

urlpatterns = [
    path('api/', include(router.urls)),
]
