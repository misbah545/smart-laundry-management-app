"""
Admin Dashboard Views for Smart Laundry System
Handles all admin-specific operations including analytics, reports, and management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from accounts.models import User, CustomerProfile
from orders.models import Order, Cloth
from complaints.models import Complaint
from feedback.models import Feedback
from payments.models import Invoice
from services.advanced_models import Service, Inventory, WorkloadPrediction, LoyaltyTransaction
from notifications.models import Notification
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_overview(request):
    """
    Get complete dashboard overview for admin
    Returns statistics, charts data, and recent activities
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Orders Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    in_process_orders = Order.objects.filter(status__in=['ASSIGNED', 'PICKED', 'IN_PROCESS']).count()
    completed_orders = Order.objects.filter(status='DELIVERED').count()
    cancelled_orders = Order.objects.filter(status='CANCELLED').count()
    
    # Today's orders
    today_orders = Order.objects.filter(order_date__date=today).count()
    
    # Revenue Statistics
    total_revenue = Invoice.objects.filter(payment_status='SUCCESS').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    today_revenue = Invoice.objects.filter(
        payment_status='SUCCESS',
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_revenue = Invoice.objects.filter(
        payment_status='SUCCESS',
        payment_date__date__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Customer Statistics
    total_customers = User.objects.filter(user_type='CUSTOMER').count()
    active_customers = User.objects.filter(
        user_type='CUSTOMER',
        customer_orders__order_date__date__gte=month_ago
    ).distinct().count()
    
    new_customers_today = User.objects.filter(
        user_type='CUSTOMER',
        date_joined__date=today
    ).count()
    
    # Complaints & Feedback
    pending_complaints = Complaint.objects.filter(status='PENDING').count()
    resolved_complaints = Complaint.objects.filter(status='RESOLVED').count()
    total_feedback = Feedback.objects.count()
    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Driver Statistics
    total_drivers = User.objects.filter(user_type='DRIVER').count()
    active_drivers = User.objects.filter(
        user_type='DRIVER',
        driver_orders__order_date__date__gte=today
    ).distinct().count()
    
    # Recent Orders
    recent_orders = Order.objects.select_related('customer', 'driver').order_by('-order_date')[:10]
    recent_orders_data = [{
        'id': order.id,
        'customer': order.customer.username,
        'status': order.status,
        'total_amount': float(order.total_amount) if order.total_amount else 0,
        'order_date': order.order_date.isoformat(),
        'driver': order.driver.username if order.driver else 'Not Assigned'
    } for order in recent_orders]
    
    # Orders by Status Chart Data
    orders_by_status = {
        'labels': ['Pending', 'In Process', 'Delivered', 'Cancelled'],
        'data': [pending_orders, in_process_orders, completed_orders, cancelled_orders]
    }
    
    # Revenue Chart Data (Last 7 days)
    revenue_chart = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_revenue = Invoice.objects.filter(
            payment_status='SUCCESS',
            payment_date__date=date
        ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_chart.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue)
        })
    
    # Inventory Alerts (Low Stock)
    low_stock_items = Inventory.objects.filter(
        quantity__lte=F('min_threshold')
    ).values('item_name', 'quantity', 'unit')[:5]
    
    # Workload Prediction for Today
    try:
        today_prediction = WorkloadPrediction.objects.filter(
            prediction_date=today
        ).first()
        predicted_orders = today_prediction.predicted_orders if today_prediction else 0
    except:
        predicted_orders = 0
    
    return Response({
        'overview': {
            'total_orders': total_orders,
            'today_orders': today_orders,
            'pending_orders': pending_orders,
            'in_process_orders': in_process_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': float(total_revenue),
            'today_revenue': float(today_revenue),
            'month_revenue': float(month_revenue),
            'total_customers': total_customers,
            'active_customers': active_customers,
            'new_customers_today': new_customers_today,
            'total_drivers': total_drivers,
            'active_drivers': active_drivers,
            'pending_complaints': pending_complaints,
            'resolved_complaints': resolved_complaints,
            'avg_rating': round(float(avg_rating), 2),
            'predicted_orders_today': predicted_orders
        },
        'charts': {
            'orders_by_status': orders_by_status,
            'revenue_last_7_days': revenue_chart
        },
        'recent_orders': recent_orders_data,
        'inventory_alerts': list(low_stock_items)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_order_qr(request):
    """
    Verify order using QR code scan
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    qr_code = request.data.get('qr_code')
    
    if not qr_code:
        return Response({"error": "QR code is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.select_related('customer', 'driver').get(qr_code=qr_code)
        
        # Get all clothes in the order
        clothes = Cloth.objects.filter(order=order)
        clothes_data = [{
            'id': cloth.id,
            'cloth_type': cloth.cloth_type,
            'fabric': cloth.fabric,
            'color': cloth.color,
            'quantity': cloth.quantity,
            'status': cloth.status,
            'qr_code': cloth.qr_code,
            'price': float(cloth.price_per_item) if cloth.price_per_item else 0
        } for cloth in clothes]
        
        return Response({
            'verified': True,
            'order': {
                'id': order.id,
                'customer': {
                    'id': order.customer.id,
                    'name': order.customer.get_full_name(),
                    'phone': order.customer.phone,
                    'email': order.customer.email
                },
                'status': order.status,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'order_date': order.order_date.isoformat(),
                'pickup_time': order.pickup_time.isoformat() if order.pickup_time else None,
                'delivery_time': order.delivery_time.isoformat() if order.delivery_time else None,
                'driver': order.driver.username if order.driver else None,
                'clothes_count': clothes.count(),
                'clothes': clothes_data
            }
        })
    except Order.DoesNotExist:
        return Response({
            'verified': False,
            'error': 'Invalid QR code'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_orders_list(request):
    """
    Return orders list for admin operations.
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    status_filter = request.query_params.get('status')

    orders_qs = Order.objects.select_related('customer', 'driver').order_by('-order_date')
    if status_filter:
        orders_qs = orders_qs.filter(status=status_filter)

    orders_data = [{
        'id': order.id,
        'status': order.status,
        'total_amount': float(order.total_amount) if order.total_amount else 0,
        'order_date': order.order_date.isoformat() if order.order_date else None,
        'pickup_time': order.pickup_time.isoformat() if order.pickup_time else None,
        'delivery_time': order.delivery_time.isoformat() if order.delivery_time else None,
        'qr_code': order.qr_code,
        'customer': {
            'id': order.customer.id,
            'username': order.customer.username,
            'email': order.customer.email,
            'phone': order.customer.phone,
        },
        'driver': {
            'id': order.driver.id,
            'username': order.driver.username,
            'phone': order.driver.phone,
        } if order.driver else None,
        'clothes_count': order.clothes.count(),
    } for order in orders_qs[:200]]

    return Response({
        'success': True,
        'count': len(orders_data),
        'orders': orders_data,
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    Update order status (Admin only)
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    new_status = request.data.get('status')
    
    if not new_status:
        return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
        
        # Create notification for customer
        Notification.objects.create(
            user=order.customer,
            title=f"Order Status Updated",
            message=f"Your order #{order.id} is now {new_status}",
            notification_type="ORDER_UPDATE"
        )
        
        return Response({
            'success': True,
            'message': 'Order status updated successfully',
            'order': {
                'id': order.id,
                'status': order.status
            }
        })
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_management(request):
    """
    Get inventory status and management data
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    # Get all inventory items
    inventory_items = Inventory.objects.all().order_by('item_name')
    
    # Calculate alerts
    low_stock = inventory_items.filter(quantity__lte=F('min_threshold'))
    critical_stock = inventory_items.filter(quantity__lte=F('min_threshold') / 2)
    
    inventory_data = [{
        'id': item.id,
        'item_name': item.item_name,
        'category': item.category,
        'current_quantity': float(item.quantity),
        'minimum_threshold': float(item.min_threshold),
        'unit': item.unit,
        'cost_per_unit': float(item.price_per_unit),
        'supplier_name': item.supplier,
        'last_restocked': item.last_restocked.isoformat() if item.last_restocked else None,
        'status': 'critical' if item in critical_stock else ('low' if item in low_stock else 'ok')
    } for item in inventory_items]
    
    return Response({
        'total_items': inventory_items.count(),
        'low_stock_count': low_stock.count(),
        'critical_stock_count': critical_stock.count(),
        'inventory': inventory_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restock_inventory(request):
    """
    Restock an inventory item
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')
    
    try:
        item = Inventory.objects.get(id=item_id)
        item.quantity += int(quantity)
        item.last_restocked = timezone.now()
        item.save()
        
        return Response({
            'success': True,
            'message': f'{item.item_name} restocked successfully',
            'new_quantity': float(item.quantity)
        })
    except Inventory.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaints_management(request):
    """
    Get all complaints with filtering options
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.query_params.get('status', None)
    
    complaints = Complaint.objects.select_related('user', 'order').all()
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    complaints = complaints.order_by('-created_at')
    
    complaints_data = [{
        'id': complaint.id,
        'customer': complaint.user.username,
        'order_id': complaint.order.id if complaint.order else None,
        'complaint_type': complaint.complaint_type,
        'subject': complaint.subject,
        'description': complaint.description,
        'status': complaint.status,
        'priority': complaint.priority,
        'created_at': complaint.created_at.isoformat(),
        'resolved_at': complaint.resolved_at.isoformat() if complaint.resolved_at else None,
        'admin_response': complaint.admin_response
    } for complaint in complaints]
    
    return Response({
        'total_complaints': complaints.count(),
        'complaints': complaints_data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def resolve_complaint(request, complaint_id):
    """
    Resolve a complaint
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    admin_response = request.data.get('response')
    
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = 'RESOLVED'
        complaint.admin_response = admin_response
        complaint.resolved_at = timezone.now()
        complaint.resolved_by = request.user
        complaint.save()
        
        # Notify customer
        Notification.objects.create(
            user=complaint.user,
            title="Complaint Resolved",
            message=f"Your complaint has been resolved: {admin_response}",
            notification_type="COMPLAINT_UPDATE"
        )
        
        return Response({
            'success': True,
            'message': 'Complaint resolved successfully'
        })
    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_reports(request):
    """
    Generate analytics and reports
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    report_type = request.query_params.get('type', 'daily')
    
    today = timezone.now().date()
    
    if report_type == 'daily':
        start_date = today
        end_date = today
    elif report_type == 'weekly':
        start_date = today - timedelta(days=7)
        end_date = today
    elif report_type == 'monthly':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today - timedelta(days=7)
        end_date = today
    
    # Orders analytics
    orders = Order.objects.filter(order_date__date__range=[start_date, end_date])
    total_orders = orders.count()
    
    # Revenue analytics
    payments = Invoice.objects.filter(
        payment_status='SUCCESS',
        payment_date__date__range=[start_date, end_date]
    )
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Service-wise breakdown
    service_stats = orders.values('clothes__cloth_type').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-count')[:10]
    
    # Peak hours analysis
    hourly_orders = orders.extra(
        select={'hour': 'EXTRACT(hour FROM order_date)'}
    ).values('hour').annotate(count=Count('id')).order_by('hour')
    
    # Customer retention
    repeat_customers = User.objects.filter(
        user_type='CUSTOMER',
        customer_orders__order_date__date__range=[start_date, end_date]
    ).annotate(
        order_count=Count('customer_orders')
    ).filter(order_count__gt=1).count()
    
    return Response({
        'report_type': report_type,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'summary': {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(total_revenue / total_orders) if total_orders > 0 else 0,
            'repeat_customers': repeat_customers
        },
        'service_breakdown': list(service_stats),
        'hourly_distribution': list(hourly_orders)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_loyalty_tracking(request):
    """
    Track customer loyalty and engagement
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    # Get top customers by loyalty points
    top_customers = CustomerProfile.objects.select_related('user').order_by('-loyalty_points')[:20]
    
    top_customers_data = [{
        'id': profile.user.id,
        'name': profile.user.get_full_name(),
        'email': profile.user.email,
        'phone': profile.user.phone,
        'loyalty_points': profile.loyalty_points,
        'total_orders': Order.objects.filter(customer=profile.user).count(),
        'total_spent': Invoice.objects.filter(
            order__customer=profile.user,
            payment_status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or 0
    } for profile in top_customers]
    
    # Recent loyalty transactions
    recent_transactions = LoyaltyTransaction.objects.select_related(
        'customer', 'order'
    ).order_by('-created_at')[:20]
    
    transactions_data = [{
        'id': trans.id,
        'customer': trans.customer.username,
        'points': trans.points,
        'transaction_type': trans.transaction_type,
        'order_id': trans.order.id if trans.order else None,
        'created_at': trans.created_at.isoformat()
    } for trans in recent_transactions]
    
    return Response({
        'top_customers': top_customers_data,
        'recent_transactions': transactions_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_driver_to_order(request):
    """
    Manually assign a driver to an order
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    order_id = request.data.get('order_id')
    driver_id = request.data.get('driver_id')
    
    try:
        order = Order.objects.get(id=order_id)
        driver = User.objects.get(id=driver_id, user_type='DRIVER')
        
        order.driver = driver
        order.status = 'ASSIGNED'
        order.save()
        
        # Notify driver
        Notification.objects.create(
            user=driver,
            title="New Order Assigned",
            message=f"You have been assigned order #{order.id}",
            notification_type="ORDER_ASSIGNED"
        )
        
        # Notify customer
        Notification.objects.create(
            user=order.customer,
            title="Driver Assigned",
            message=f"Driver {driver.get_full_name()} has been assigned to your order",
            notification_type="ORDER_UPDATE"
        )
        
        return Response({
            'success': True,
            'message': 'Driver assigned successfully'
        })
    except (Order.DoesNotExist, User.DoesNotExist):
        return Response({"error": "Order or Driver not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workload_prediction(request):
    """
    Get AI-based workload prediction
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    # Get predictions for next 7 days
    today = timezone.now().date()
    predictions = []
    
    for i in range(7):
        date = today + timedelta(days=i)
        try:
            prediction = WorkloadPrediction.objects.filter(prediction_date=date).first()
            if prediction:
                predictions.append({
                    'date': date.isoformat(),
                    'predicted_orders': prediction.predicted_orders,
                    'confidence': float(prediction.confidence),
                    'recommended_staff': prediction.staff_recommendation
                })
            else:
                # If no prediction, use historical average
                avg_orders = Order.objects.filter(
                    order_date__week_day=date.isoweekday()
                ).count() // 52  # Rough average
                
                predictions.append({
                    'date': date.isoformat(),
                    'predicted_orders': avg_orders,
                    'confidence': 0.7,
                    'recommended_staff': max(2, avg_orders // 10)
                })
        except:
            predictions.append({
                'date': date.isoformat(),
                'predicted_orders': 0,
                'confidence': 0,
                'recommended_staff': 2
            })
    
    return Response({
        'predictions': predictions
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_discount_or_refund(request):
    """
    Apply discount or process refund for a customer
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    action_type = request.data.get('type')  # 'discount' or 'refund'
    order_id = request.data.get('order_id')
    amount = request.data.get('amount')
    reason = request.data.get('reason')
    
    try:
        order = Order.objects.get(id=order_id)
        
        if action_type == 'discount':
            order.discount_applied = float(amount)
            order.total_amount = float(order.total_amount) - float(amount)
            order.save()
            
            message = f"Discount of ₹{amount} applied to your order #{order.id}"
            
        elif action_type == 'refund':
            # Process refund logic here
            invoice = Invoice.objects.filter(order=order, payment_status='SUCCESS').first()
            if invoice:
                invoice.payment_status = 'REFUNDED'
                invoice.save()
                
            message = f"Refund of ₹{amount} processed for order #{order.id}"
        
        # Notify customer
        Notification.objects.create(
            user=order.customer,
            title=f"{action_type.title()} Applied",
            message=f"{message}. Reason: {reason}",
            notification_type="PAYMENT_UPDATE"
        )
        
        return Response({
            'success': True,
            'message': f'{action_type.title()} applied successfully'
        })
        
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_customers_list(request):
    """
    Get list of all customers with their details
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    customers = User.objects.filter(user_type='CUSTOMER').select_related('customerprofile')
    
    customers_data = []
    for customer in customers:
        try:
            profile = customer.customerprofile
            loyalty_points = profile.loyalty_points
        except:
            loyalty_points = 0
        
        total_orders = Order.objects.filter(customer=customer).count()
        total_spent = Invoice.objects.filter(
            order__customer=customer,
            payment_status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        customers_data.append({
            'id': customer.id,
            'name': customer.get_full_name(),
            'email': customer.email,
            'phone': customer.phone,
            'is_active': customer.is_active,
            'joined_date': customer.date_joined.isoformat(),
            'total_orders': total_orders,
            'total_spent': float(total_spent),
            'loyalty_points': loyalty_points
        })
    
    return Response({
        'total_customers': len(customers_data),
        'customers': customers_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_drivers_list(request):
    """
    Get list of all drivers with their performance metrics
    """
    if request.user.user_type != 'ADMIN':
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    drivers = User.objects.filter(user_type='DRIVER')
    
    drivers_data = []
    for driver in drivers:
        total_deliveries = Order.objects.filter(driver=driver, status='DELIVERED').count()
        active_orders = Order.objects.filter(
            driver=driver,
            status__in=['ASSIGNED', 'PICKED', 'IN_PROCESS']
        ).count()
        
        avg_rating = Feedback.objects.filter(order__driver=driver).aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        drivers_data.append({
            'id': driver.id,
            'name': driver.get_full_name(),
            'email': driver.email,
            'phone': driver.phone,
            'is_active': driver.is_active,
            'joined_date': driver.date_joined.isoformat(),
            'total_deliveries': total_deliveries,
            'active_orders': active_orders,
            'avg_rating': round(float(avg_rating), 2)
        })
    
    return Response({
        'total_drivers': len(drivers_data),
        'drivers': drivers_data
    })
