# consumers.py

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from elearn_app.models import ChatMessage
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send chat history to the user upon connection
        chat_history = await self.get_chat_history()
        for message in chat_history:
            await self.send(text_data=json.dumps({
                'message': message['message'],
                'sender': message['sender'],
                'auth_group': message['auth_group'],
                'timestamp': message['timestamp'],
                'type': 'chat'  # Mark as a normal chat message
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_username = text_data_json['sender']
        auth_group = text_data_json['auth_group']
        message_type = text_data_json.get('type', 'chat')  # Default to 'chat'

        # Save the message to the database if it's a chat message
        if message_type == 'chat':
            sender = await self.get_user(text_data_json['user_id'])
            if sender:
                await database_sync_to_async(ChatMessage.objects.create)(
                    room_name=self.room_name,
                    sender=sender,
                    message=message
                )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'auth_group': auth_group,
                'timestamp': '',
                'message_type': message_type
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender']
        auth_group = event['auth_group']
        message_type = event.get('message_type', 'chat')

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_username,
            'auth_group': auth_group,
            'message_type': message_type
        }))

    @database_sync_to_async
    def get_chat_history(self):
        messages = ChatMessage.objects.filter(room_name=self.room_name).order_by('timestamp')
        return [{
            'message': message.message,
            'sender': message.sender.username,
            'auth_group': message.sender.groups.first().name if message.sender.groups.exists() else 'student',
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for message in messages]

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            print(f"User with id {user_id} does not exist.")
            return None

    @database_sync_to_async
    def save_chat_message(self, room_name, sender, message):
        return ChatMessage.objects.create(room_name=room_name, sender=sender, message=message)
