from rest_framework import serializers
from .models import AIPrediction


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
