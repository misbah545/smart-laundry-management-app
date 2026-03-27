import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from messaging.models import Message, ChatRoom
from accounts.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        recipient_id = data.get('recipient_id')
        
        if not message_text or not recipient_id:
            return
        
        # Save message to database
        message = await self.save_message(message_text, recipient_id)
        
        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'timestamp': message.timestamp.isoformat(),
            }
        )
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def save_message(self, content, recipient_id):
        """Save message to database"""
        try:
            recipient = User.objects.get(id=recipient_id)
            message = Message.objects.create(
                sender=self.user,
                recipient=recipient,
                content=content,
            )
            return message
        except User.DoesNotExist:
            return None
