from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Complaint, Feedback
from .serializers import ComplaintSerializer, FeedbackSerializer

# -------------------------
# Complaint ViewSet
# -------------------------
class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter complaints by customer
    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        status_filter = self.request.query_params.get('status')
        qs = self.queryset
        if customer_id:
            qs = qs.filter(customer__id=customer_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark complaint as resolved"""
        complaint = self.get_object()
        complaint.status = 'RESOLVED'
        complaint.save()
        return Response({'status': 'Complaint resolved'})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get complaint statistics"""
        stats = {
            'total_complaints': Complaint.objects.count(),
            'by_status': Complaint.objects.values('status').annotate(count=Count('id')),
            'by_issue_type': Complaint.objects.values('issue_type').annotate(count=Count('id')),
        }
        return Response(stats)

# -------------------------
# Feedback ViewSet
# -------------------------
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter feedback by customer or order
    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        order_id = self.request.query_params.get('order_id')
        qs = self.queryset
        if customer_id:
            qs = qs.filter(customer__id=customer_id)
        if order_id:
            qs = qs.filter(order__id=order_id)
        return qs
