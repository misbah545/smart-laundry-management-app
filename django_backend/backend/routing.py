from django.urls import re_path
from messaging.consumers import ChatConsumer
from tracking.consumers import LocationConsumer, OrderUpdatesConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/location/(?P<order_id>\d+)/$', LocationConsumer.as_asgi()),
    re_path(r'ws/orders/(?P<user_id>\d+)/$', OrderUpdatesConsumer.as_asgi()),
]
