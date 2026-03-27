from rest_framework import serializers
from messaging.models import Message, ChatRoom
from accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'recipient', 'recipient_name', 'order', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source='message_set')
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'room_id', 'participants', 'order', 'messages', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'room_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        messages = obj.message_set.all()[:1]
        if messages:
            return MessageSerializer(messages[0]).data
        return None
