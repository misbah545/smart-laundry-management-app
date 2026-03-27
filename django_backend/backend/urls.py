from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    # Django Admin panel
    path('admin/', admin.site.urls),
    
    # Custom Admin Panel API
    path('api/admin/', include('backend.admin_urls')),

    # Accounts / Authentication
    path('api/accounts/', include('accounts.urls')),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Other apps APIs
    path('api/orders/', include('orders.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/feedbacks/', include('feedback.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/invoices/', include('payments.urls')),
    path('api/chatbot/', include('services.urls')),
    path('api/ai/', include('ai_predictions.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/tracking/', include('tracking.urls')),
]
