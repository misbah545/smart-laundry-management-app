from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('api/', include(router.urls)),
]
