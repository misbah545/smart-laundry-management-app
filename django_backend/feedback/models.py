from django.db import models
from orders.models import Order
from accounts.models import User


class Feedback(models.Model):
    FEEDBACK_TYPE = [
        ('SERVICE', 'Service'),
        ('DRIVER', 'Driver'),
        ('APP', 'App'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_feedbacks')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_feedbacks')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_feedbacks')
    rating = models.IntegerField()
    comments = models.TextField()
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order'], name='feedback_order_idx'),
            models.Index(fields=['customer'], name='feedback_customer_idx'),
            models.Index(fields=['driver'], name='feedback_driver_idx'),
            models.Index(fields=['rating'], name='feedback_rating_idx'),
            models.Index(fields=['-created_at'], name='feedback_recent_idx'),
            models.Index(fields=['rating', '-created_at'], name='feedback_rating_date_idx'),
        ]

    def __str__(self):
        return f"Feedback #{self.id}"
