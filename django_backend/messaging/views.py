from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from messaging.models import Message, ChatRoom
from messaging.serializers import MessageSerializer, ChatRoomSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user))
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a message to another user"""
        recipient_id = request.data.get('recipient_id')
        content = request.data.get('content')
        order_id = request.data.get('order_id')
        
        if not recipient_id or not content:
            return Response({'error': 'recipient_id and content required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from accounts.models import User
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
            order_id=order_id,
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation with a specific user"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        messages = Message.objects.filter(
            Q(sender=request.user, recipient_id=user_id) |
            Q(sender_id=user_id, recipient=request.user)
        ).order_by('timestamp')
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark message as read"""
        message = self.get_object()
        if message.recipient != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        message.is_read = True
        message.save()
        return Response({'status': 'Message marked as read'})


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_room(self, request):
        """Create or get chat room with another user"""
        other_user_id = request.data.get('user_id')
        order_id = request.data.get('order_id')
        
        if not other_user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from accounts.models import User
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Find or create room
        room = ChatRoom.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).first()
        
        if not room:
            room = ChatRoom.objects.create(order_id=order_id)
            room.participants.add(request.user, other_user)
        
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a chat room"""
        room = self.get_object()
        messages = room.message_set.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
