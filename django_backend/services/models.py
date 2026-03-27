from django.db import models
from accounts.models import User
from orders.models import Order

class ChatbotLog(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    sentiment = models.CharField(max_length=20, blank=True, null=True)  # POSITIVE, NEGATIVE, NEUTRAL
    auto_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}"


class AIPrediction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='service_ai_predictions')
    prediction_type = models.CharField(max_length=50)
    predicted_value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.id}"


# Import advanced models
from .advanced_models import (
    Service, ClothRecognition, DigitalInvoice, LoyaltyTransaction,
    Inventory, WorkloadPrediction, PriceEstimate, Discount
)
