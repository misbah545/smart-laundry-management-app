from rest_framework import viewsets, permissions
from .models import AIPrediction
from .serializers import AIPredictionSerializer

# -------------------------
# AIPrediction ViewSet
# -------------------------
class AIPredictionViewSet(viewsets.ModelViewSet):
    queryset = AIPrediction.objects.all()
    serializer_class = AIPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access

    # Optional: filter by order ID
    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        if order_id:
            return self.queryset.filter(order__id=order_id)
        return self.queryset
