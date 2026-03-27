from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatbotLogViewSet, AIPredictionViewSet
from . import advanced_views

router = DefaultRouter()
router.register(r'chatbot-logs', ChatbotLogViewSet, basename='chatbotlog')
router.register(r'ai-predictions-old', AIPredictionViewSet, basename='aiprediction')

urlpatterns = [
    path('api/', include(router.urls)),
    
    # OTP/2FA Authentication
    path('api/auth/send-otp/', advanced_views.send_otp, name='send-otp'),
    path('api/auth/verify-otp/', advanced_views.verify_otp, name='verify-otp'),
    
    # AI Cloth Recognition
    path('api/ai/recognize-cloth/', advanced_views.recognize_cloth, name='recognize-cloth'),
    
    # ML Price Estimation
    path('api/ai/estimate-price/', advanced_views.estimate_price, name='estimate-price'),
    
    # QR Code Generation
    path('api/qr/generate/', advanced_views.generate_qr_codes, name='generate-qr'),
    
    # Digital Invoice
    path('api/invoice/generate/', advanced_views.generate_invoice, name='generate-invoice'),
    
    # Loyalty Points
    path('api/loyalty/add-points/', advanced_views.add_loyalty_points, name='add-loyalty-points'),
    path('api/loyalty/redeem-points/', advanced_views.redeem_loyalty_points, name='redeem-loyalty-points'),
    
    # AI Workload Prediction
    path('api/ai/predict-workload/', advanced_views.predict_workload, name='predict-workload'),
    
    # Inventory Management
    path('api/inventory/check/', advanced_views.check_inventory, name='check-inventory'),
    
    # Admin Stats
    path('api/admin/stats/', advanced_views.admin_stats, name='admin-stats'),
]
