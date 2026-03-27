from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, DeviceToken
from .serializers import NotificationSerializer, DeviceTokenSerializer
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

# -------------------------
# Helper: Send Expo Push Notification
# -------------------------
def send_push_notification(user, title, body, data=None):
    """
    Send push notification to a user via Expo Push Service
    
    Args:
        user: User instance
        title: Notification title
        body: Notification body
        data: Optional dict of extra data
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # Get all device tokens for this user
    tokens = DeviceToken.objects.filter(user=user, platform='expo').values_list('token', flat=True)
    
    if not tokens:
        return False
    
    # Build push messages
    messages = []
    for token in tokens:
        try:
            messages.append(PushMessage(
                to=token,
                title=title,
                body=body,
                data=data or {},
                sound='default',
                priority='high',
            ))
        except Exception as e:
            print(f"Error building message for token {token}: {e}")
            continue
    
    if not messages:
        return False
    
    # Send via Expo
    try:
        client = PushClient()
        tickets = client.publish_multiple(messages)
        
        # Check for errors and remove invalid tokens
        for i, ticket in enumerate(tickets):
            if ticket.get('status') == 'error':
                error_type = ticket.get('details', {}).get('error')
                if error_type == 'DeviceNotRegistered':
                    # Remove invalid token
                    DeviceToken.objects.filter(token=list(tokens)[i]).delete()
                    
        return True
        
    except (PushServerError, ConnectionError, HTTPError) as e:
        print(f"Push notification failed: {e}")
        return False

# -------------------------
# Notification ViewSet
# -------------------------
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Optional: filter notifications by user
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        is_read = self.request.query_params.get('is_read')
        qs = self.queryset
        if user_id:
            qs = qs.filter(user__id=user_id)
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')
        return qs.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for a user"""
        user_id = request.data.get('user_id')
        if user_id:
            Notification.objects.filter(user__id=user_id, is_read=False).update(is_read=True)
            return Response({'status': 'All notifications marked as read'})
        return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def register_token(self, request):
        """Register or update device token for push notifications"""
        token = request.data.get('token')
        platform = request.data.get('platform', 'expo')

        if not token:
            return Response({'error': 'token required'}, status=status.HTTP_400_BAD_REQUEST)

        device_token, _ = DeviceToken.objects.update_or_create(
            token=token,
            defaults={'user': request.user, 'platform': platform},
        )

        serializer = DeviceTokenSerializer(device_token)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def send_push(self, request):
        """
        Send push notification to specific user(s)
        
        Body params:
        - user_id: int (optional, defaults to request.user)
        - title: str
        - body: str
        - data: dict (optional)
        """
        from accounts.models import User
        
        user_id = request.data.get('user_id', request.user.id)
        title = request.data.get('title')
        body = request.data.get('body')
        data = request.data.get('data', {})
        
        if not title or not body:
            return Response({'error': 'title and body required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        success = send_push_notification(user, title, body, data)
        
        if success:
            # Also save to database
            Notification.objects.create(
                user=user,
                title=title,
                message=body,
            )
            return Response({'status': 'Push notification sent'})
        else:
            return Response({'error': 'No device tokens found or send failed'}, status=status.HTTP_400_BAD_REQUEST)
