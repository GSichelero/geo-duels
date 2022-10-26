import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from users.models import FriendRequest, Room, RoomMember, RoomConfig, Round, Guessings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        self.password = self.scope["query_string"].decode("utf-8").split("password=")[1].split("&")[0]
        self.nickname = self.scope["query_string"].decode("utf-8").split("username=")[1]

        self.room = await sync_to_async(Room.objects.using('nonrel').get)(room_name=self.room_name, room_password=self.password)

        if any(user['username'] == self.nickname for user in self.room.room_members):
            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))