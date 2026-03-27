from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from .models import Order, Cloth, DriverLocation
from .serializers import OrderSerializer, ClothSerializer, DriverLocationSerializer

# -------------------------
# Order ViewSet
# -------------------------
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter by customer or driver
    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        driver_id = self.request.query_params.get('driver_id')
        status_filter = self.request.query_params.get('status')
        qs = self.queryset
        if customer_id:
            qs = qs.filter(customer__id=customer_id)
        if driver_id:
            qs = qs.filter(driver__id=driver_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-order_date')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        from notifications.views import send_push_notification
        from notifications.models import Notification
        
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Send push notification to customer
            if order.customer:
                title = f"Order #{order.id} Updated"
                body = f"Your order status changed from {old_status} to {new_status}"
                send_push_notification(
                    order.customer,
                    title,
                    body,
                    {'order_id': order.id, 'status': new_status}
                )
                
                # Also save to database
                Notification.objects.create(
                    user=order.customer,
                    title=title,
                    message=body,
                )
            
            return Response({'status': 'Order status updated', 'new_status': new_status})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get order statistics"""
        stats = {
            'total_orders': Order.objects.count(),
            'by_status': Order.objects.values('status').annotate(count=Count('id')),
            'total_revenue': Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0,
            'average_order_value': Order.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0,
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def customer_orders(self, request):
        """Get orders for the current user if they're a customer"""
        orders = Order.objects.filter(customer=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def driver_orders(self, request):
        """Get orders assigned to the current user if they're a driver"""
        orders = Order.objects.filter(driver=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_driver_location(self, request):
        """
        Update driver location for active order
        
        Body params:
        - order_id: int (optional)
        - latitude: float
        - longitude: float
        """
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        order_id = request.data.get('order_id')
        
        if not latitude or not longitude:
            return Response({'error': 'latitude and longitude required'}, status=status.HTTP_400_BAD_REQUEST)
        
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id, driver=request.user)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
        
        location = DriverLocation.objects.create(
            driver=request.user,
            order=order,
            latitude=latitude,
            longitude=longitude,
        )
        
        serializer = DriverLocationSerializer(location)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def driver_location(self, request, pk=None):
        """
        Get latest driver location for an order
        """
        order = self.get_object()
        
        if not order.driver:
            return Response({'error': 'No driver assigned'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get most recent location for this order
        location = DriverLocation.objects.filter(order=order).first()
        
        if not location:
            # Fallback: get driver's most recent location across all orders
            location = DriverLocation.objects.filter(driver=order.driver).first()
        
        if location:
            serializer = DriverLocationSerializer(location)
            return Response(serializer.data)
        else:
            return Response({'error': 'No location data available'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def upload_pickup_proof(self, request, pk=None):
        """Upload photo proof of pickup"""
        from django.utils import timezone
        
        order = self.get_object()
        
        if 'image' not in request.FILES:
            return Response({'error': 'image required'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.pickup_proof = request.FILES['image']
        order.pickup_proof_timestamp = timezone.now()
        order.save()
        
        return Response({'status': 'Pickup proof uploaded'})

    @action(detail=True, methods=['post'])
    def upload_delivery_proof(self, request, pk=None):
        """Upload photo proof of delivery"""
        from django.utils import timezone
        
        order = self.get_object()
        
        if 'image' not in request.FILES:
            return Response({'error': 'image required'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.delivery_proof = request.FILES['image']
        order.delivery_proof_timestamp = timezone.now()
        order.status = 'DELIVERED'  # Auto-mark as delivered
        order.save()
        
        # Send notification
        from notifications.views import send_push_notification
        send_push_notification(
            order.customer,
            "Order Delivered",
            f"Your order #{order.id} has been delivered!",
            {'order_id': order.id}
        )
        
        return Response({'status': 'Delivery proof uploaded'})


# -------------------------
# Cloth ViewSet
# -------------------------
class ClothViewSet(viewsets.ModelViewSet):
    queryset = Cloth.objects.all()
    serializer_class = ClothSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter by order
    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        cloth_status = self.request.query_params.get('status')
        qs = self.queryset
        if order_id:
            qs = qs.filter(order__id=order_id)
        if cloth_status:
            qs = qs.filter(status=cloth_status)
        return qs

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update cloth status"""
        cloth = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Cloth.STATUS_CHOICES):
            cloth.status = new_status
            cloth.save()
            return Response({'status': 'Cloth status updated', 'new_status': new_status})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
