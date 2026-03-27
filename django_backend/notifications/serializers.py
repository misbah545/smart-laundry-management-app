from rest_framework import serializers
from .models import Notification, DeviceToken


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'message',
            'user',
            'is_read',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = [
            'id',
            'user',
            'token',
            'platform',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
