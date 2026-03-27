from django.db import models
from accounts.models import User
from orders.models import Order, Cloth

# ===========================
# Service Catalog
# ===========================
class Service(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('WASH', 'Wash'),
        ('DRY_CLEAN', 'Dry Clean'),
        ('IRON', 'Iron'),
        ('FOLD', 'Fold'),
        ('STEAM', 'Steam'),
    )
    
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - ${self.base_price}"


# ===========================
# AI Cloth Recognition
# ===========================
class ClothRecognition(models.Model):
    FABRIC_CHOICES = (
        ('COTTON', 'Cotton'),
        ('POLYESTER', 'Polyester'),
        ('SILK', 'Silk'),
        ('WOOL', 'Wool'),
        ('LINEN', 'Linen'),
        ('DENIM', 'Denim'),
        ('SYNTHETIC', 'Synthetic'),
    )
    
    cloth = models.OneToOneField(Cloth, on_delete=models.CASCADE, related_name='recognition')
    image = models.ImageField(upload_to='cloth_images/', blank=True, null=True)
    
    # AI Detection Results
    detected_type = models.CharField(max_length=50, blank=True, null=True)
    detected_fabric = models.CharField(max_length=20, choices=FABRIC_CHOICES, blank=True, null=True)
    detected_color = models.CharField(max_length=30, blank=True, null=True)
    confidence_score = models.FloatField(default=0.0)
    
    # AI Recommendations
    recommended_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    recommended_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recognition for {self.cloth.cloth_type}"


# ===========================
# Digital Invoice
# ===========================
class DigitalInvoice(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='digital_invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - ${self.total_amount}"


# ===========================
# Loyalty Program
# ===========================
class LoyaltyTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('EARNED', 'Earned'),
        ('REDEEMED', 'Redeemed'),
        ('EXPIRED', 'Expired'),
    )
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loyalty_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.username} - {self.points} points {self.transaction_type}"


# ===========================
# Inventory Management
# ===========================
class Inventory(models.Model):
    CATEGORY_CHOICES = (
        ('DETERGENT', 'Detergent'),
        ('SOFTENER', 'Softener'),
        ('PACKAGING', 'Packaging'),
        ('EQUIPMENT', 'Equipment'),
        ('OTHER', 'Other'),
    )
    
    item_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, default='units')
    min_threshold = models.IntegerField(default=10)
    
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.quantity} {self.unit}"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_threshold


# ===========================
# AI Workload Prediction
# ===========================
class WorkloadPrediction(models.Model):
    prediction_date = models.DateField()
    predicted_orders = models.IntegerField()
    predicted_workload = models.CharField(max_length=20)  # LOW, MEDIUM, HIGH
    confidence = models.FloatField(default=0.0)
    
    staff_recommendation = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction for {self.prediction_date} - {self.predicted_orders} orders"


# ===========================
# Price Estimation (ML)
# ===========================
class PriceEstimate(models.Model):
    cloth_type = models.CharField(max_length=50)
    fabric = models.CharField(max_length=20)
    service_type = models.CharField(max_length=20)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cloth_type} - ${self.estimated_price}"


# ===========================
# Discount & Promotions
# ===========================
class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
        ('LOYALTY', 'Loyalty Points'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    times_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.value}{'%' if self.discount_type == 'PERCENTAGE' else '$'}"
