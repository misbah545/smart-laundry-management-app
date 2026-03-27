from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import stripe

from orders.models import Order
from .models import StripeCustomer
from .models import Invoice
from .serializers import InvoiceSerializer

# -------------------------
# Invoice ViewSet
# -------------------------
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter invoices by order
    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        payment_status = self.request.query_params.get('payment_status')
        customer_id = self.request.query_params.get('customer_id')
        qs = self.queryset
        if order_id:
            qs = qs.filter(order__id=order_id)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        if customer_id:
            qs = qs.filter(order__customer__id=customer_id)
        return qs


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_intent(request):
    """Create Stripe PaymentIntent and return client secret"""
    if not settings.STRIPE_SECRET_KEY:
        return Response(
            {'error': 'Stripe secret key not configured'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order_id = request.data.get('order_id')
    currency = request.data.get('currency') or settings.STRIPE_CURRENCY
    payment_method_id = request.data.get('payment_method_id')

    if not order_id:
        return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    amount = order.total_amount or 0
    if amount <= 0:
        return Response({'error': 'Order amount invalid'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        stripe_customer, _ = StripeCustomer.objects.get_or_create(
            user=order.customer,
            defaults={'customer_id': stripe.Customer.create(email=order.customer.email or None).id},
        )

        intent_params = {
            'amount': int(float(amount) * 100),
            'currency': currency,
            'customer': stripe_customer.customer_id,
            'metadata': {
                'order_id': str(order.id),
                'customer_id': str(order.customer_id),
            },
            'automatic_payment_methods': {'enabled': True},
        }

        if payment_method_id:
            intent_params.update(
                {
                    'payment_method': payment_method_id,
                    'confirm': True,
                    'off_session': False,
                }
            )

        intent = stripe.PaymentIntent.create(**intent_params)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    Invoice.objects.update_or_create(
        order=order,
        defaults={
            'amount': order.total_amount or 0,
            'payment_mode': 'STRIPE',
            'payment_status': 'PENDING',
            'payment_intent_id': intent.id,
        },
    )

    return Response(
        {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': float(amount),
            'currency': currency,
            'status': intent.status,
            'requires_action': intent.status == 'requires_action',
            'customer_id': stripe_customer.customer_id,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        }
    )


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhooks and update invoice payment status"""
    if not settings.STRIPE_WEBHOOK_SECRET:
        return Response(
            {'error': 'Stripe webhook secret not configured'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    if not sig_header:
        return Response({'error': 'Missing Stripe signature'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    event_type = event.get('type')
    data_object = event.get('data', {}).get('object', {})
    metadata = data_object.get('metadata', {})
    order_id = metadata.get('order_id')

    if event_type in ['payment_intent.succeeded', 'payment_intent.payment_failed', 'payment_intent.canceled']:
        if not order_id:
            return Response({'error': 'order_id not found in metadata'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        payment_status = 'SUCCESS' if event_type == 'payment_intent.succeeded' else 'FAILED'

        invoice, _ = Invoice.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total_amount or 0,
                'payment_mode': 'STRIPE',
            },
        )

        invoice.payment_status = payment_status
        invoice.payment_date = timezone.now()
        invoice.payment_mode = 'STRIPE'
        invoice.payment_intent_id = data_object.get('id') or invoice.payment_intent_id
        if not invoice.amount:
            invoice.amount = order.total_amount or 0
        invoice.save()

        # Update order status based on payment result
        if payment_status == 'SUCCESS' and order.status == 'PENDING':
            order.status = 'IN_PROCESS'
            order.save()
        elif payment_status == 'FAILED' and order.status == 'PENDING':
            order.status = 'CANCELLED'
            order.save()

    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_stripe_customer(request):
    """Create or return Stripe customer for current user"""
    if not settings.STRIPE_SECRET_KEY:
        return Response({'error': 'Stripe secret key not configured'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    customer, created = StripeCustomer.objects.get_or_create(
        user=request.user,
        defaults={
            'customer_id': stripe.Customer.create(email=request.user.email or None).id
        },
    )

    return Response({'customer_id': customer.customer_id, 'created': created})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_setup_intent(request):
    """Create SetupIntent for saving a card"""
    if not settings.STRIPE_SECRET_KEY:
        return Response({'error': 'Stripe secret key not configured'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    customer, _ = StripeCustomer.objects.get_or_create(
        user=request.user,
        defaults={
            'customer_id': stripe.Customer.create(email=request.user.email or None).id
        },
    )

    intent = stripe.SetupIntent.create(
        customer=customer.customer_id,
        payment_method_types=['card'],
    )

    return Response({'client_secret': intent.client_secret, 'customer_id': customer.customer_id})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_payment_methods(request):
    """List saved card payment methods"""
    if not settings.STRIPE_SECRET_KEY:
        return Response({'error': 'Stripe secret key not configured'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    customer = StripeCustomer.objects.filter(user=request.user).first()
    if not customer:
        return Response({'payment_methods': []})

    payment_methods = stripe.PaymentMethod.list(
        customer=customer.customer_id,
        type='card',
    )

    return Response({'payment_methods': payment_methods.data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def detach_payment_method(request):
    """Detach a saved card"""
    if not settings.STRIPE_SECRET_KEY:
        return Response({'error': 'Stripe secret key not configured'}, status=status.HTTP_400_BAD_REQUEST)

    payment_method_id = request.data.get('payment_method_id')
    if not payment_method_id:
        return Response({'error': 'payment_method_id required'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        payment_method = stripe.PaymentMethod.detach(payment_method_id)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detached': True, 'payment_method_id': payment_method.id})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refund_payment(request):
    """Refund a Stripe payment by order_id or payment_intent_id"""
    if not settings.STRIPE_SECRET_KEY:
        return Response(
            {'error': 'Stripe secret key not configured'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order_id = request.data.get('order_id')
    payment_intent_id = request.data.get('payment_intent_id')
    amount = request.data.get('amount')

    if not order_id and not payment_intent_id:
        return Response(
            {'error': 'order_id or payment_intent_id required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    invoice = None
    order = None
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        invoice = Invoice.objects.filter(order=order).first()
        payment_intent_id = payment_intent_id or (invoice.payment_intent_id if invoice else None)

    if not payment_intent_id:
        return Response({'error': 'payment_intent_id not available'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        refund_params = {'payment_intent': payment_intent_id}
        if amount:
            refund_params['amount'] = int(float(amount) * 100)
        refund = stripe.Refund.create(**refund_params)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if invoice:
        invoice.payment_status = 'REFUNDED'
        invoice.payment_date = timezone.now()
        invoice.payment_mode = 'STRIPE'
        invoice.payment_intent_id = payment_intent_id
        if not invoice.amount and order:
            invoice.amount = order.total_amount or 0
        invoice.save()

    if order and order.status != 'CANCELLED':
        order.status = 'CANCELLED'
        order.save()

    return Response(
        {
            'refund_id': refund.id,
            'status': refund.status,
            'payment_intent_id': payment_intent_id,
        }
    )
