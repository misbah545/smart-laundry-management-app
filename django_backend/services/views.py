from rest_framework import viewsets, permissions
from .models import ChatbotLog, AIPrediction
from .serializers import ChatbotLogSerializer, AIPredictionSerializer

# -------------------------
# ChatbotLog ViewSet
# -------------------------
class ChatbotLogViewSet(viewsets.ModelViewSet):
    queryset = ChatbotLog.objects.all()
    serializer_class = ChatbotLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter by customer
    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        qs = self.queryset
        if customer_id:
            qs = qs.filter(customer__id=customer_id)
        return qs


# -------------------------
# AIPrediction ViewSet
# -------------------------
class AIPredictionViewSet(viewsets.ModelViewSet):
    queryset = AIPrediction.objects.all()
    serializer_class = AIPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter by order
    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        qs = self.queryset
        if order_id:
            qs = qs.filter(order__id=order_id)
        return qs
