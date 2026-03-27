from django.contrib import admin
from .advanced_models import (
    Service, ClothRecognition, DigitalInvoice, LoyaltyTransaction,
    Inventory, WorkloadPrediction, PriceEstimate, Discount
)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'base_price', 'is_active']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name']


@admin.register(ClothRecognition)
class ClothRecognitionAdmin(admin.ModelAdmin):
    list_display = ['cloth', 'detected_type', 'detected_fabric', 'confidence_score', 'created_at']
    list_filter = ['detected_fabric', 'detected_type']
    search_fields = ['cloth__cloth_type']


@admin.register(DigitalInvoice)
class DigitalInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['payment_status', 'payment_method']
    search_fields = ['invoice_number', 'transaction_id']
    readonly_fields = ['invoice_number', 'created_at']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'transaction_type', 'points', 'order', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['customer__username']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'quantity', 'min_threshold', 'is_low_stock']
    list_filter = ['category']
    search_fields = ['item_name']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True


@admin.register(WorkloadPrediction)
class WorkloadPredictionAdmin(admin.ModelAdmin):
    list_display = ['prediction_date', 'predicted_orders', 'predicted_workload', 'staff_recommendation', 'confidence']
    list_filter = ['predicted_workload']


@admin.register(PriceEstimate)
class PriceEstimateAdmin(admin.ModelAdmin):
    list_display = ['cloth_type', 'fabric', 'service_type', 'estimated_price', 'confidence', 'created_at']
    list_filter = ['fabric', 'service_type']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'is_active', 'valid_from', 'valid_until', 'times_used']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']
