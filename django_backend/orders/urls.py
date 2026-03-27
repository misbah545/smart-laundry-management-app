from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ClothViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'clothes', ClothViewSet, basename='cloth')

urlpatterns = [
    path('api/', include(router.urls)),
]
