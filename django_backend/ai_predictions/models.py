from django.db import models
from orders.models import Order


class AIPrediction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ai_predictions')
    prediction_type = models.CharField(max_length=50)
    predicted_value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction #{self.id}"
