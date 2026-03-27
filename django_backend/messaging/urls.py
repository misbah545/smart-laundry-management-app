from django.urls import path, include
from rest_framework.routers import DefaultRouter
from messaging.views import MessageViewSet, ChatRoomViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)),
]
