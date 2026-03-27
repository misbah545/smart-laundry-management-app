from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id',
            'order',
            'amount',
            'payment_mode',
            'payment_status',
            'payment_intent_id',
            'payment_date'
        ]
        read_only_fields = ['id']
