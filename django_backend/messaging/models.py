from django.db import models
from accounts.models import User
from orders.models import Order

class Message(models.Model):
    """Chat messages between users"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'recipient', '-timestamp']),
            models.Index(fields=['order', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.content[:50]}"


class ChatRoom(models.Model):
    """Chat room between two users"""
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_room')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['order'], name='chatroom_order_idx'),
            models.Index(fields=['-updated_at'], name='chatroom_recent_idx'),
        ]
    
    def __str__(self):
        return f"ChatRoom {self.id}"
    
    @property
    def room_id(self):
        return f"chat_{self.id}"
