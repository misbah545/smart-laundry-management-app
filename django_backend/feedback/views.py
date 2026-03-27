from rest_framework import viewsets, permissions
from .models import Feedback
from .serializers import FeedbackSerializer

# -------------------------
# Feedback ViewSet
# -------------------------
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter feedback by customer, order, or driver
    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        order_id = self.request.query_params.get('order_id')
        driver_id = self.request.query_params.get('driver_id')
        
        qs = self.queryset
        if customer_id:
            qs = qs.filter(customer__id=customer_id)
        if order_id:
            qs = qs.filter(order__id=order_id)
        if driver_id:
            qs = qs.filter(driver__id=driver_id)
        return qs
