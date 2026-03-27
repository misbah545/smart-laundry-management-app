from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
        ('DRIVER', 'Driver'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # OTP/2FA fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    
    # Fingerprint authentication
    fingerprint_enabled = models.BooleanField(default=False)
    fingerprint_token = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    house_no = models.CharField(max_length=50)
    street_name = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    landmark = models.CharField(max_length=100, blank=True, null=True)

    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="India")

    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)

    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class DriverProfile(models.Model):

    AVAILABILITY_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('BUSY', 'Busy'),
        ('OFFLINE', 'Offline'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_no = models.CharField(max_length=50)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='AVAILABLE')

    def __str__(self):
        return self.user.username
