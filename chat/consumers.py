import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Channel, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', 'chat_message') 
        user = self.scope["user"]

        if action == 'chat_message':

            if user.is_authenticated and user.is_blocked:
                return
            message = data.get('message', '')
            image_url = data.get('image_url', None)
            message_id = data.get('message_id', None) 

            if user.is_authenticated and not image_url and message:
                message_id = await self.save_message(user, self.room_name, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_event',
                    'message': message,
                    'image_url': image_url,
                    'username': user.username if user.is_authenticated else "Anonim",
                    'message_id': message_id
                }
            )

        elif action == 'delete_message':
            message_id = data.get('message_id')
            if user.is_authenticated:
                success = await self.delete_message_db(user, message_id)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_deleted_event',
                            'message_id': message_id
                        }
                    )

    async def chat_message_event(self, event):
        await self.send(text_data=json.dumps({
            'action': 'chat_message',
            'message': event['message'],
            'image_url': event.get('image_url'),
            'username': event['username'],
            'message_id': event['message_id']
        }))

    async def message_deleted_event(self, event):
        await self.send(text_data=json.dumps({
            'action': 'delete_message',
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def save_message(self, user, room_name, message_content):
        channel, _ = Channel.objects.get_or_create(name=room_name)
        msg = Message.objects.create(sender=user, channel=channel, content=message_content)
        return msg.id

    @database_sync_to_async
    def delete_message_db(self, user, message_id):
        try:
            msg = Message.objects.get(id=message_id)
            if msg.sender == user or user.role in ['admin', 'mod']:
                msg.delete()
                return True
        except Message.DoesNotExist:
            pass
        return False