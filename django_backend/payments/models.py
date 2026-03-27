from django.db import models
from orders.models import Order

class Invoice(models.Model):

    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')

    payment_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['order'], name='invoice_order_idx'),
            models.Index(fields=['payment_status'], name='invoice_status_idx'),
            models.Index(fields=['payment_date'], name='invoice_date_idx'),
            models.Index(fields=['payment_status', '-payment_date'], name='invoice_status_date_idx'),
        ]

    def __str__(self):
        return f"Invoice {self.order.id}"


class StripeCustomer(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StripeCustomer {self.user_id}"
