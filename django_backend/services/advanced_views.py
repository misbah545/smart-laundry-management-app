"""
Advanced API Views for Smart Laundry
Includes AI/ML features, OTP authentication, QR code, invoices, etc.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta, datetime
import random
import string
import hashlib

from accounts.models import User, CustomerProfile
from orders.models import Order, Cloth
from services.advanced_models import (
    Service, ClothRecognition, DigitalInvoice, LoyaltyTransaction,
    Inventory, WorkloadPrediction, PriceEstimate, Discount
)


# ===========================
# OTP/2FA Authentication
# ===========================
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    """Send OTP to phone number for verification"""
    phone = request.data.get('phone')
    
    if not phone:
        return Response({'error': 'Phone number required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    try:
        user = User.objects.get(phone=phone)
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        
        # In production, send SMS via Twilio/AWS SNS
        # For now, return OTP in response (ONLY FOR TESTING!)
        return Response({
            'message': 'OTP sent successfully',
            'otp': otp,  # Remove this in production!
            'phone': phone
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    """Verify OTP and mark phone as verified"""
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    
    if not phone or not otp:
        return Response({'error': 'Phone and OTP required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(phone=phone)
        
        # Check if OTP expired (5 minutes)
        if user.otp_created_at and (timezone.now() - user.otp_created_at).seconds > 300:
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.otp == otp:
            user.is_phone_verified = True
            user.otp = None  # Clear OTP after verification
            user.save()
            return Response({'message': 'Phone verified successfully', 'verified': True})
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# ===========================
# AI Cloth Recognition
# ===========================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def recognize_cloth(request):
    """Upload cloth image and get AI recognition results"""
    cloth_id = request.data.get('cloth_id')
    image = request.FILES.get('image')
    
    if not cloth_id:
        return Response({'error': 'cloth_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        cloth = Cloth.objects.get(id=cloth_id)
        
        # Create or update recognition record
        recognition, created = ClothRecognition.objects.get_or_create(cloth=cloth)
        
        if image:
            recognition.image = image
        
        # Mock AI Detection (In production, use TensorFlow/PyTorch model)
        fabric_types = ['COTTON', 'POLYESTER', 'SILK', 'WOOL', 'LINEN']
        cloth_types = ['Shirt', 'Pants', 'Dress', 'Jacket', 'Sweater']
        colors = ['White', 'Black', 'Blue', 'Red', 'Green']
        
        recognition.detected_type = random.choice(cloth_types)
        recognition.detected_fabric = random.choice(fabric_types)
        recognition.detected_color = random.choice(colors)
        recognition.confidence_score = round(random.uniform(0.85, 0.99), 2)
        
        # Update cloth with detected values
        cloth.cloth_type = recognition.detected_type
        cloth.fabric = recognition.detected_fabric
        cloth.color = recognition.detected_color
        cloth.save()
        
        # Get service recommendation
        service_recommendation = get_service_recommendation(recognition.detected_fabric)
        recognition.recommended_service = service_recommendation
        recognition.save()
        
        return Response({
            'cloth_id': cloth.id,
            'detected_type': recognition.detected_type,
            'detected_fabric': recognition.detected_fabric,
            'detected_color': recognition.detected_color,
            'confidence': recognition.confidence_score,
            'recommended_service': service_recommendation.name if service_recommendation else None,
            'message': 'Cloth recognized successfully'
        })
        
    except Cloth.DoesNotExist:
        return Response({'error': 'Cloth not found'}, status=status.HTTP_404_NOT_FOUND)


def get_service_recommendation(fabric):
    """AI-based service recommendation based on fabric type"""
    # Get or create default services
    if fabric in ['SILK', 'WOOL']:
        service, _ = Service.objects.get_or_create(
            service_type='DRY_CLEAN',
            defaults={'name': 'Dry Cleaning', 'base_price': 15.00}
        )
    elif fabric == 'COTTON':
        service, _ = Service.objects.get_or_create(
            service_type='WASH',
            defaults={'name': 'Regular Wash', 'base_price': 5.00}
        )
    else:
        service, _ = Service.objects.get_or_create(
            service_type='STEAM',
            defaults={'name': 'Steam Clean', 'base_price': 10.00}
        )
    return service


# ===========================
# ML Price Estimation
# ===========================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def estimate_price(request):
    """Estimate price using ML model"""
    cloth_type = request.data.get('cloth_type')
    fabric = request.data.get('fabric', 'COTTON')
    service_type = request.data.get('service_type', 'WASH')
    weight = request.data.get('weight', 1.0)
    
    # Mock ML prediction (In production, use trained ML model)
    base_prices = {
        'WASH': 5.00,
        'DRY_CLEAN': 15.00,
        'IRON': 3.00,
        'STEAM': 10.00
    }
    
    fabric_multipliers = {
        'SILK': 2.0,
        'WOOL': 1.8,
        'COTTON': 1.0,
        'LINEN': 1.2,
        'POLYESTER': 0.9
    }
    
    base = base_prices.get(service_type, 5.00)
    multiplier = fabric_multipliers.get(fabric, 1.0)
    estimated_price = round(base * multiplier * float(weight), 2)
    
    # Save estimate
    estimate = PriceEstimate.objects.create(
        cloth_type=cloth_type,
        fabric=fabric,
        service_type=service_type,
        weight=weight,
        estimated_price=estimated_price,
        confidence=0.92
    )
    
    return Response({
        'cloth_type': cloth_type,
        'fabric': fabric,
        'service_type': service_type,
        'weight': weight,
        'estimated_price': estimated_price,
        'confidence': 0.92,
        'message': 'Price estimated successfully'
    })


# ===========================
# QR Code Generation
# ===========================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_qr_codes(request):
    """Generate QR codes for order and all clothes"""
    order_id = request.data.get('order_id')
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Generate order QR code
        if not order.qr_code:
            order.qr_code = f"ORD-{order.id}-{hashlib.md5(str(order.id).encode()).hexdigest()[:8].upper()}"
            order.save()
        
        # Generate QR codes for each cloth
        cloth_qr_codes = []
        for cloth in order.clothes.all():
            if not cloth.qr_code:
                cloth.qr_code = f"CLT-{cloth.id}-{hashlib.md5(str(cloth.id).encode()).hexdigest()[:8].upper()}"
                cloth.save()
            cloth_qr_codes.append({
                'cloth_id': cloth.id,
                'cloth_type': cloth.cloth_type,
                'qr_code': cloth.qr_code
            })
        
        return Response({
            'order_id': order.id,
            'order_qr_code': order.qr_code,
            'clothes_qr_codes': cloth_qr_codes,
            'message': 'QR codes generated successfully'
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


# ===========================
# Digital Invoice Generation
# ===========================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_invoice(request):
    """Generate digital invoice for an order"""
    order_id = request.data.get('order_id')
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Check if invoice already exists
        if hasattr(order, 'digital_invoice'):
            invoice = order.digital_invoice
        else:
            # Calculate totals
            subtotal = sum([
                (cloth.price_per_item or 0) * cloth.quantity 
                for cloth in order.clothes.all()
            ])
            
            discount = order.discount_applied
            tax = round(subtotal * 0.18, 2)  # 18% GST
            total = round(subtotal - discount + tax, 2)
            
            # Generate invoice number
            invoice_num = f"INV-{datetime.now().year}-{order.id:06d}"
            
            # Create invoice
            invoice = DigitalInvoice.objects.create(
                order=order,
                invoice_number=invoice_num,
                subtotal=subtotal,
                discount=discount,
                tax=tax,
                total_amount=total,
                payment_status='PENDING'
            )
            
            # Update order total
            order.total_amount = total
            order.save()
        
        return Response({
            'invoice_number': invoice.invoice_number,
            'order_id': order.id,
            'customer': order.customer.username,
            'subtotal': float(invoice.subtotal),
            'discount': float(invoice.discount),
            'tax': float(invoice.tax),
            'total_amount': float(invoice.total_amount),
            'payment_status': invoice.payment_status,
            'created_at': invoice.created_at,
            'message': 'Invoice generated successfully'
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


# ===========================
# Loyalty Points Management
# ===========================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_loyalty_points(request):
    """Award loyalty points after order completion"""
    order_id = request.data.get('order_id')
    
    try:
        order = Order.objects.get(id=order_id)
        customer = order.customer
        customer_profile = customer.customerprofile
        
        # Calculate points (1 point per $1 spent)
        points_earned = int(order.total_amount or 0)
        
        # Add points to customer
        customer_profile.loyalty_points += points_earned
        customer_profile.save()
        
        # Log transaction
        LoyaltyTransaction.objects.create(
            customer=customer,
            order=order,
            transaction_type='EARNED',
            points=points_earned,
            description=f"Earned from Order #{order.id}"
        )
        
        return Response({
            'points_earned': points_earned,
            'total_points': customer_profile.loyalty_points,
            'message': f'{points_earned} loyalty points added'
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def redeem_loyalty_points(request):
    """Redeem loyalty points for discount"""
    points_to_redeem = request.data.get('points', 0)
    order_id = request.data.get('order_id')
    
    try:
        customer = request.user
        customer_profile = customer.customerprofile
        
        if points_to_redeem > customer_profile.loyalty_points:
            return Response({'error': 'Insufficient points'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Redeem points (100 points = $10)
        discount_amount = (points_to_redeem / 100) * 10
        
        customer_profile.loyalty_points -= points_to_redeem
        customer_profile.save()
        
        # Apply to order if provided
        if order_id:
            order = Order.objects.get(id=order_id)
            order.loyalty_points_used = points_to_redeem
            order.discount_applied += discount_amount
            order.save()
        
        # Log transaction
        LoyaltyTransaction.objects.create(
            customer=customer,
            order_id=order_id,
            transaction_type='REDEEMED',
            points=-points_to_redeem,
            description=f"Redeemed {points_to_redeem} points for ${discount_amount}"
        )
        
        return Response({
            'points_redeemed': points_to_redeem,
            'discount_amount': discount_amount,
            'remaining_points': customer_profile.loyalty_points,
            'message': 'Points redeemed successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ===========================
# AI Workload Prediction
# ===========================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def predict_workload(request):
    """Predict workload for next 7 days using ML"""
    predictions = []
    
    # Get historical data
    total_orders = Order.objects.count()
    avg_daily_orders = total_orders / 30 if total_orders > 0 else 5
    
    for days_ahead in range(1, 8):
        prediction_date = (datetime.now() + timedelta(days=days_ahead)).date()
        
        # Mock ML prediction (in production, use actual ML model)
        # Add some randomness to simulate real predictions
        predicted_orders = int(avg_daily_orders * random.uniform(0.7, 1.3))
        
        if predicted_orders < 5:
            workload = 'LOW'
            staff_needed = 2
        elif predicted_orders < 15:
            workload = 'MEDIUM'
            staff_needed = 4
        else:
            workload = 'HIGH'
            staff_needed = 6
        
        prediction = WorkloadPrediction.objects.create(
            prediction_date=prediction_date,
            predicted_orders=predicted_orders,
            predicted_workload=workload,
            confidence=0.88,
            staff_recommendation=staff_needed
        )
        
        predictions.append({
            'date': prediction_date,
            'predicted_orders': predicted_orders,
            'workload': workload,
            'staff_recommendation': staff_needed,
            'confidence': 0.88
        })
    
    return Response({
        'predictions': predictions,
        'message': 'Workload predicted for next 7 days'
    })


# ===========================
# Inventory Management
# ===========================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_inventory(request):
    """Check inventory status and low stock items"""
    low_stock_items = []
    all_items = Inventory.objects.all()
    
    for item in all_items:
        if item.is_low_stock:
            low_stock_items.append(item)
    
    return Response({
        'total_items': all_items.count(),
        'low_stock_count': len(low_stock_items),
        'low_stock_items': [
            {
                'id': item.id,
                'name': item.item_name,
                'category': item.category,
                'quantity': item.quantity,
                'min_threshold': item.min_threshold,
                'status': 'CRITICAL' if item.quantity < item.min_threshold / 2 else 'LOW'
            }
            for item in low_stock_items
        ]
    })


# ===========================
# Admin Dashboard Statistics
# ===========================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_stats(request):
    """Aggregate KPIs for the Admin Dashboard in Flutter"""
    today = timezone.now().date()
    
    # Revenue Calculation
    total_rev = Order.objects.aggregate(res=Sum('total_amount'))['res'] or 0.0
    
    # Weekly Revenue Trend (Last 7 Days)
    weekly_rev_data = []
    for days_back in range(6, -1, -1):
        target_date = today - timedelta(days=days_back)
        day_rev = Order.objects.filter(
            created_at__date=target_date
        ).aggregate(res=Sum('total_amount'))['res'] or random.uniform(20.0, 99.0) # Mock numbers if DB empty
        weekly_rev_data.append(float(day_rev))

    # General Counts
    total_orders_count = Order.objects.count()
    low_stock = Inventory.objects.filter(quantity__lt=20).count()
    
    # (Assuming Complaints uses Feedback model for now as a makeshift logic in this view)
    from feedback.models import Feedback
    complaints_count = Feedback.objects.filter(rating__lt=3).count()
    
    return Response({
        'totalRevenue': float(total_rev),
        'totalOrders': total_orders_count,
        'complaints': complaints_count,
        'lowStockItems': low_stock,
        'weeklyRevenue': weekly_rev_data,
    })
