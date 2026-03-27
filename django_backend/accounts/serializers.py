from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, CustomerProfile, DriverProfile


# -------------------------
# Custom JWT Token Serializer
# -------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_type'] = user.user_type
        token['username'] = user.username
        token['email'] = user.email
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra user info to response
        data['user_type'] = self.user.user_type
        data['username'] = self.user.username
        data['user_id'] = self.user.id
        
        return data


# -------------------------
# Customer Profile Serializer
# -------------------------

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = [
            'house_no',
            'street_name',
            'area',
            'landmark',
            'city',
            'state',
            'pincode',
            'country',
            'latitude',
            'longitude',
            'loyalty_points'
        ]


# -------------------------
# Driver Profile Serializer
# -------------------------

class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ['vehicle_no', 'availability']


# -------------------------
# Register Serializer (Nested)
# -------------------------

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    customer_profile = CustomerProfileSerializer(required=False)
    driver_profile = DriverProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'user_type',
            'fingerprint_enabled',
            'fingerprint_token',
            'customer_profile',
            'driver_profile'
        ]

    def create(self, validated_data):

        customer_data = validated_data.pop('customer_profile', None)
        driver_data = validated_data.pop('driver_profile', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            fingerprint_enabled=validated_data.get('fingerprint_enabled', False),
            fingerprint_token=validated_data.get('fingerprint_token')
        )

        # Create Customer Profile
        if user.user_type == "CUSTOMER" and customer_data:
            CustomerProfile.objects.create(user=user, **customer_data)

        # Create Driver Profile
        if user.user_type == "DRIVER" and driver_data:
            DriverProfile.objects.create(user=user, **driver_data)

        return user


# -------------------------
# User Serializer (Safe View)
# -------------------------

class UserSerializer(serializers.ModelSerializer):

    customer_profile = CustomerProfileSerializer(read_only=True)
    driver_profile = DriverProfileSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ['password']
