from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet,
    create_payment_intent,
    stripe_webhook,
    refund_payment,
    create_stripe_customer,
    create_setup_intent,
    list_payment_methods,
    detach_payment_method,
)

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('create-intent/', create_payment_intent),
    path('refund/', refund_payment),
    path('webhook/', stripe_webhook),
    path('stripe/customer/', create_stripe_customer),
    path('stripe/setup-intent/', create_setup_intent),
    path('stripe/payment-methods/', list_payment_methods),
    path('stripe/detach/', detach_payment_method),
    path('api/', include(router.urls)),
]
