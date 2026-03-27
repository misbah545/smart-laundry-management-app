from rest_framework import serializers
from .models import Order, Cloth, DriverLocation


class ClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = [
            'id',
            'order',
            'cloth_type',
            'color',
            'quantity',
            'image_url',
            'qr_code',
            'status',
            'special_instruction'
        ]


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ['id', 'driver', 'order', 'latitude', 'longitude', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class OrderSerializer(serializers.ModelSerializer):
    clothes = ClothSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'driver',
            'status',
            'total_amount',
            'pickup_proof',
            'delivery_proof',
            'order_date',
            'clothes'
        ]
        read_only_fields = ['id', 'order_date']
