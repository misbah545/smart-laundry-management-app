from rest_framework import serializers
from services.advanced_models import (
    Service, ClothRecognition, DigitalInvoice, LoyaltyTransaction,
    Inventory, WorkloadPrediction, PriceEstimate, Discount
)
from orders.models import Cloth


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ClothRecognitionSerializer(serializers.ModelSerializer):
    cloth_type = serializers.CharField(source='cloth.cloth_type', read_only=True)
    
    class Meta:
        model = ClothRecognition
        fields = ['id', 'cloth', 'cloth_type', 'image', 'detected_type', 
                 'detected_fabric', 'detected_color', 'confidence_score',
                 'recommended_service', 'recommended_price', 'created_at']


class DigitalInvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='order.customer.get_full_name', read_only=True)
    order_date = serializers.DateTimeField(source='order.order_date', read_only=True)
    
    class Meta:
        model = DigitalInvoice
        fields = '__all__'


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    
    class Meta:
        model = LoyaltyTransaction
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'


class WorkloadPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkloadPrediction
        fields = '__all__'


class PriceEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceEstimate
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    
    def get_is_valid(self, obj):
        from django.utils import timezone
        now = timezone.now()
        return (obj.is_active and 
                obj.valid_from <= now <= obj.valid_until and
                (obj.usage_limit is None or obj.times_used < obj.usage_limit))
    
    class Meta:
        model = Discount
        fields = '__all__'
