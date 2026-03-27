from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIPredictionViewSet

router = DefaultRouter()
router.register(r'ai-predictions', AIPredictionViewSet, basename='aiprediction')

urlpatterns = [
    path('api/', include(router.urls)),
]
