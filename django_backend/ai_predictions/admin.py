from django.contrib import admin
from .models import AIPrediction  # correct import

@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'prediction_type', 'predicted_value', 'created_at')
    list_filter = ('prediction_type', 'created_at')
    search_fields = ('order__id', 'predicted_value')
