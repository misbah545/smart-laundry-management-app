from django.db import models
from accounts.models import User

class Order(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('PICKED', 'Picked'),
        ('IN_PROCESS', 'In Process'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="driver_orders")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points_used = models.IntegerField(default=0)
    
    # Scheduling
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)

    # Proofs
    pickup_proof = models.ImageField(upload_to='proofs/pickup/', blank=True, null=True)
    pickup_proof_timestamp = models.DateTimeField(blank=True, null=True)
    
    delivery_proof = models.ImageField(upload_to='proofs/delivery/', blank=True, null=True)
    delivery_proof_timestamp = models.DateTimeField(blank=True, null=True)
    
    # Tracking
    qr_code = models.CharField(max_length=255, blank=True, null=True, unique=True)

    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['status'], name='order_status_idx'),
            models.Index(fields=['customer'], name='order_customer_idx'),
            models.Index(fields=['driver'], name='order_driver_idx'),
            models.Index(fields=['order_date'], name='order_date_idx'),
            models.Index(fields=['customer', 'status'], name='order_customer_status_idx'),
            models.Index(fields=['driver', '-order_date'], name='order_driver_recent_idx'),
        ]

    def __str__(self):
        return f"Order {self.id}"

class DriverLocation(models.Model):
    """
    Real-time location tracking for drivers
    """
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver_locations')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='driver_locations')
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # ETA and route optimization
    eta_minutes = models.IntegerField(null=True, blank=True)  # Estimated time in minutes
    distance_remaining_km = models.FloatField(null=True, blank=True)  # Remaining distance
    
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['driver', '-timestamp']),
            models.Index(fields=['order', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Driver {self.driver.id} - {self.latitude},{self.longitude} at {self.timestamp}"

class Cloth(models.Model):

    STATUS_CHOICES = (
        ('RECEIVED', 'Received'),
        ('IN_WASH', 'In Wash'),
        ('IRONING', 'Ironing'),
        ('DELIVERED', 'Delivered'),
        ('MISSING', 'Missing'),
    )
    
    FABRIC_CHOICES = (
        ('COTTON', 'Cotton'),
        ('POLYESTER', 'Polyester'),
        ('SILK', 'Silk'),
        ('WOOL', 'Wool'),
        ('LINEN', 'Linen'),
        ('DENIM', 'Denim'),
        ('SYNTHETIC', 'Synthetic'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="clothes")

    cloth_type = models.CharField(max_length=50)
    fabric = models.CharField(max_length=20, choices=FABRIC_CHOICES, blank=True, null=True)
    color = models.CharField(max_length=30)
    quantity = models.IntegerField(default=1)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    image_url = models.TextField(blank=True, null=True)
    qr_code = models.CharField(max_length=255, blank=True, null=True, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')

    special_instruction = models.CharField(max_length=255, blank=True, null=True)
    
    # Pricing
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.cloth_type} - {self.order.id}"
