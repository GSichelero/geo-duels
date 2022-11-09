from datetime import datetime, timedelta
import json
from users.serializers import RoomSerializer

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from users.models import FriendRequest, Room, RoomMember, RoomConfig, Round, Guessings


def get_dict_from_list(list_of_dicts, key, value):
    return next((item for item in list_of_dicts if item[key] == value), None)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        self.password = self.scope["query_string"].decode("utf-8").split("password=")[1].split("&")[0]
        self.nickname = self.scope["query_string"].decode("utf-8").split("username=")[1]

        self.room = await sync_to_async(Room.objects.using('nonrel').get)(room_name=self.room_name, room_password=self.password)

        if any(user['username'] == self.nickname for user in self.room.room_members):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message","room": self.room})


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        current_time = datetime.utcnow()
        self.room = await sync_to_async(Room.objects.using('nonrel').get)(room_name=self.room_name, room_password=self.password)

        if self.room.room_state == "waiting":
            print(self.room)
            if "ready" in text_data_json:
                for user in self.room.room_members:
                    if user["username"] == self.nickname:
                        user["is_ready"] = True
                        break
                await sync_to_async(self.room.save)(using='nonrel')
            print(self.room, all(user["is_ready"] for user in self.room.room_members), len(self.room.room_members) == self.room.room_configs["max_members"])
            if all(user["is_ready"] for user in self.room.room_members) and len(self.room.room_members) == self.room.room_configs["max_members"]:
                # move to picking phase, round 1
                self.room.room_state = "picking"
                self.room.room_deadline_time = (current_time + timedelta(seconds=self.room.room_configs["time_per_pick"])).timestamp()
                self.room.room_round = 1
                self.room.player_turn = 0
                for user in self.room.room_members:
                    user["rounds"].append({
                        "id": 1,
                        "round_number": self.room.room_round,
                        "guessings": [],
                        "picking": {
                            "id": 1,
                            "lat": None,
                            "lng": None,
                        }
                    })
                await sync_to_async(self.room.save)(using='nonrel')
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message","room": self.room})


        elif self.room.room_state == "picking":
            if current_time.timestamp() <= self.room.room_deadline_time:
                if "pick" in text_data_json:
                    for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] = text_data_json["pick"]["lat"]
                            get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lng"] = text_data_json["pick"]["lng"]
                            break
                    await sync_to_async(self.room.save)(using='nonrel')

            if current_time.timestamp() > self.room.room_deadline_time and not all(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] for user in self.room.room_members):
                for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            if not get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"]:
                                get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] = 0
                                get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lng"] = 0
            if current_time.timestamp() > self.room.room_deadline_time or all(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] for user in self.room.room_members):
                # move to guessing phase, player_turn 1
                self.room.room_state = "guessing"
                self.room.room_deadline_time = (current_time + timedelta(seconds=self.room.room_configs["time_per_guess"])).timestamp()
                self.room.player_turn = 1
                for user in self.room.room_members:
                    get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"].append({
                        "id": 1,
                        "guess_number": self.room.player_turn,
                        "guess_geopoint": {
                            "id": 1,
                            "lat": None,
                            "lng": None,
                        }
                    })
                await sync_to_async(self.room.save)(using='nonrel')
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message","room": self.room})

        
        elif self.room.room_state == "guessing":
            if current_time.timestamp() <= self.room.room_deadline_time:
                if "guess" in text_data_json:
                    for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = text_data_json["guess"]["lat"]
                            get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lng"] = text_data_json["guess"]["lng"]
                            break
                    await sync_to_async(self.room.save)(using='nonrel')

            if current_time.timestamp() > self.room.room_deadline_time and not all(get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] for user in self.room.room_members):
                for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            if not get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"]:
                                get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = 0
                                get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = 0
            
            if current_time.timestamp() > self.room.room_deadline_time or all(get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] for user in self.room.room_members):
                if self.room.player_turn < self.room.room_configs["max_members"]:
                    # move to guessing phase, next player_turn
                    self.room.player_turn = self.room.player_turn + 1
                    self.room.room_deadline_time = (current_time + timedelta(seconds=self.room.room_configs["time_per_guess"])).timestamp()
                    for user in self.room.room_members:
                        get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"].append({
                            "id": 1,
                            "guess_number": self.room.player_turn,
                            "guess_geopoint": {
                                "id": 1,
                                "lat": None,
                                "lng": None,
                            }
                        })
                elif self.room.player_turn == self.room.room_configs["max_members"] and self.room.room_round < self.room.room_configs["number_of_rounds"]:
                    # move to picking phase, next round
                    self.room.room_state = "picking"
                    self.room.room_deadline_time = (current_time + timedelta(seconds=self.room.room_configs["time_per_pick"])).timestamp()
                    self.room.room_round = self.room.room_round + 1
                    for user in self.room.room_members:
                        user["rounds"].append({
                            "id": 1,
                            "round_number": self.room.room_round,
                            "guessings": [],
                            "picking": {
                                "id": 1,
                                "lat": None,
                                "lng": None,
                            }
                        })
                else:
                    # move to endgame phase
                    self.room.room_state = "endgame"

                await sync_to_async(self.room.save)(using='nonrel')
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message","room": self.room})


    async def chat_message(self, event):
        print(event)
        room = event["room"]
        
        await self.send(text_data=json.dumps({"room": RoomSerializer(room).data}))