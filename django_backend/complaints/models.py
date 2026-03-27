from django.db import models
from accounts.models import User
from orders.models import Order

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('RESOLVED', 'Resolved'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order'], name='complaint_order_idx'),
            models.Index(fields=['customer'], name='complaint_customer_idx'),
            models.Index(fields=['status'], name='complaint_status_idx'),
            models.Index(fields=['-created_at'], name='complaint_recent_idx'),
            models.Index(fields=['status', '-created_at'], name='complaint_status_date_idx'),
        ]

    def __str__(self):
        return f"Complaint {self.id}"


class Feedback(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaint_feedbacks')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='complaint_feedbacks')
    rating = models.IntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order'], name='cmp_fb_order_idx'),
            models.Index(fields=['customer'], name='cmp_fb_cust_idx'),
            models.Index(fields=['rating'], name='cmp_fb_rating_idx'),
            models.Index(fields=['-created_at'], name='cmp_fb_recent_idx'),
        ]

    def __str__(self):
        return f"Feedback {self.id}"
