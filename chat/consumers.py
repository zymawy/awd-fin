import json
from typing import List, Dict, Optional
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from urjwan_app.models import ChatMessage
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        chat_history = await self.get_chat_history()
        for message in chat_history:
            await self.send(text_data=json.dumps({
                'message': message['message'],
                'sender': message['sender'],
                'auth_group': message['auth_group'],
                'timestamp': message['timestamp'],
                'type': 'chat'
            }))

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']
        auth_group = data['auth_group']
        message_type = data.get('type', 'chat')

        if message_type == 'chat':
            sender = await self.get_user(data['user_id'])
            if sender:
                await self.save_chat_message(self.room_name, sender, message)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
            'sender': sender_username,
            'auth_group': auth_group,
            'timestamp': '',
            'message_type': message_type
        })

    async def chat_message(self, event: Dict[str, str]) -> None:
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'auth_group': event['auth_group'],
            'message_type': event.get('message_type', 'chat')
        }))

    @database_sync_to_async
    def get_chat_history(self) -> List[Dict[str, str]]:
        return [
            {
                'message': msg.message,
                'sender': msg.sender.username,
                'auth_group': msg.sender.groups.first().name if msg.sender.groups.exists() else 'student',
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for msg in ChatMessage.objects.filter(room_name=self.room_name).order_by('timestamp')
        ]

    @database_sync_to_async
    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_chat_message(self, room_name: str, sender: User, message: str) -> ChatMessage:
        return ChatMessage.objects.create(room_name=room_name, sender=sender, message=message)
