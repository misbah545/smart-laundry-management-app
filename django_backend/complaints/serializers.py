from rest_framework import serializers
from .models import Complaint, Feedback


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id',
            'order',
            'customer',
            'issue_type',
            'description',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id',
            'customer',
            'order',
            'rating',
            'comments',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
