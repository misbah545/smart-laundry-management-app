from rest_framework import serializers
from .models import ChatbotLog, AIPrediction


class ChatbotLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotLog
        fields = [
            'id',
            'customer',
            'query',
            'response',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AIPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrediction
        fields = [
            'id',
            'order',
            'prediction_type',
            'predicted_value',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
