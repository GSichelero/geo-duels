from datetime import datetime, timedelta
import json
import random
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
        self.current_time = datetime.utcnow()

        if any(user['username'] == self.nickname for user in self.room.room_members):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": self.current_time.timestamp()})


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        current_time = datetime.utcnow()
        self.room = await sync_to_async(Room.objects.using('nonrel').get)(room_name=self.room_name, room_password=self.password)
        if self.room.room_state == "waiting":
            if "ready" in text_data_json:
                for user in self.room.room_members:
                    if user["username"] == self.nickname:
                        user["is_ready"] = True
                        break
                await sync_to_async(self.room.save)(using='nonrel')
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
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})


        elif self.room.room_state == "picking":
            if current_time.timestamp() <= self.room.room_deadline_time:
                if "pick" in text_data_json:
                    for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] = text_data_json["pick"]["lat"]
                            get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lng"] = text_data_json["pick"]["lng"]
                            break
                    await sync_to_async(self.room.save)(using='nonrel')

            if current_time.timestamp() >= self.room.room_deadline_time and not all(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] for user in self.room.room_members):
                for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            if not get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"]:
                                get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] = 0
                                get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lng"] = 0
            if current_time.timestamp() >= self.room.room_deadline_time or all(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["picking"]["lat"] for user in self.room.room_members):
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
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})

        
        elif self.room.room_state == "guessing":
            if current_time.timestamp() <= self.room.room_deadline_time:
                if "guess" in text_data_json:
                    for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = text_data_json["guess"]["lat"]
                            get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lng"] = text_data_json["guess"]["lng"]
                            break
                    await sync_to_async(self.room.save)(using='nonrel')

            if current_time.timestamp() >= self.room.room_deadline_time and not all(get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] for user in self.room.room_members):
                for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            if not get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"]:
                                get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = 0
                                get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = 0
            
            if current_time.timestamp() >= self.room.room_deadline_time or all(get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] for user in self.room.room_members):
                # move to results phase
                self.room.room_state = "results"
                self.room.room_deadline_time = (current_time + timedelta(seconds=15)).timestamp()
                await sync_to_async(self.room.save)(using='nonrel')
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})
        
        elif self.room.room_state == "results":
            if current_time.timestamp() >= self.room.room_deadline_time:
                if self.room.player_turn < self.room.room_configs["max_members"]:
                    # move to guessing phase, next player_turn
                    self.room.room_state = "guessing"
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
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})


    async def chat_message(self, event):
        room = event["room"]
        
        await self.send(text_data=json.dumps({"room": RoomSerializer(room).data, "current_time": event["current_time"]}))



class SinglePlayerMatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        self.nickname = self.scope["query_string"].decode("utf-8").split("username=")[1]

        self.room = await sync_to_async(Room.objects.using('nonrel').get)(room_name=self.room_name)
        self.current_time = datetime.utcnow()

        if any(user['username'] == self.nickname for user in self.room.room_members):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": self.current_time.timestamp()})


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        current_time = datetime.utcnow()
        self.room = await sync_to_async(Room.objects.using('nonrel').get)(room_name=self.room_name)

        places = [
        (40.6892, -74.0445),   # Statue of Liberty, New York City, USA
        (48.8584, 2.2945),     # Eiffel Tower, Paris, France
        (27.1751, 78.0421),    # Taj Mahal, Agra, India
        (40.4319, 116.5704),   # Great Wall of China, China
        (-33.8568, 151.2153),  # Sydney Opera House, Sydney, Australia
        (-22.9519, -43.2105),  # Christ the Redeemer, Rio de Janeiro, Brazil
        (-13.1631, -72.5450),  # Machu Picchu, Cusco Region, Peru
        (41.8902, 12.4922),    # Colosseum, Rome, Italy
        (29.9792, 31.1342),    # Great Pyramid of Giza, Egypt
        (30.3285, 35.4419),    # Petra, Jordan
        (37.9715, 23.7267),    # Acropolis of Athens, Greece
        (27.9881, 86.9250),    # Mount Everest, Nepal/China Border
        (13.4125, 103.8660),   # Angkor Wat, Siem Reap, Cambodia
        (43.0828, -79.0742),   # Niagara Falls, Ontario, Canada/New York, USA
        (51.1789, -1.8262),    # Stonehenge, Wiltshire, England
        (25.6953, -54.4367),   # Iguazu Falls, Paraná, Brazil/Argentina
        (19.4326, -99.1332),   # Teotihuacan, Mexico
        (51.5007, -0.1246),    # Buckingham Palace, London, England
        (48.8566, 2.3522),     # Notre-Dame Cathedral, Paris, France
        (29.9792, 31.1342),    # Sphinx of Giza, Egypt
        (19.9333, 32.5333),    # Nile River, Egypt
        (27.1749, 78.0421),    # Agra Fort, Agra, India
        (61.0636, -7.1881),    # Strokkur Geyser, Geysir, Iceland
        (35.7101, 139.8107),   # Tokyo Tower, Tokyo, Japan
        (51.1789, -1.8262),    # Avebury, Wiltshire, England
        (48.8584, 2.2945),     # Palace of Versailles, Versailles, France
        (51.1789, -1.8262),    # Salisbury Cathedral, Salisbury, England
        (27.9861, 86.9223),    # Khumbu Icefall, Mount Everest, Nepal
        (55.7517, 37.6178),    # Red Square, Moscow, Russia
        (30.3285, 35.4419)     # Wadi Rum, Jordan
        ]

        five_places = random.sample(places, 5)

        if self.room.room_state == "waiting":
            self.room.room_state = "guessing"
            self.room.room_deadline_time = (current_time + timedelta(seconds=self.room.room_configs["time_per_guess"])).timestamp()
            self.room.room_round = 1
            self.room.player_turn = 2
            self.room.room_members.append({
                'id': 1,
                'user_number': 2,
                'username': 'Computer',
                'score': 0,
                'is_ready': True,
                'rounds': [],
            })
            for user in self.room.room_members:
                if user["username"] == 'Computer':
                    for i in range(1, self.room.room_configs["number_of_rounds"]+1):
                        user["rounds"].append({
                            "id": 1,
                            "round_number": i,
                            "guessings": [
                                {
                                    "id": 1,
                                    "guess_number": 1,
                                    "guess_geopoint": {
                                        "id": 1,
                                        "lat": 27,
                                        "lng": 27,
                                    }
                                },
                                {
                                    "id": 1,
                                    "guess_number": 2,
                                    "guess_geopoint": {
                                        "id": 1,
                                        "lat": 27,
                                        "lng": 27,
                                    }
                                },
                            ],
                            "picking": {
                                "id": 1,
                                "lat": five_places[i-1][0],
                                "lng": five_places[i-1][1],
                            }
                        })
                else:
                    for i in range(1, self.room.room_configs["number_of_rounds"]+1):
                        user["rounds"].append({
                            "id": 1,
                            "round_number": i,
                            "guessings": [
                                {
                                    "id": 1,
                                    "guess_number": 1,
                                    "guess_geopoint": {
                                        "id": 1,
                                        "lat": 27,
                                        "lng": 27,
                                    }
                                },
                                {
                                    "id": 1,
                                    "guess_number": 2,
                                    "guess_geopoint": {
                                        "id": 1,
                                        "lat": None,
                                        "lng": None,
                                    }
                                },
                            ],
                            "picking": {
                                "id": 1,
                                "lat": 27,
                                "lng": 27,
                            }
                        })
            await sync_to_async(self.room.save)(using='nonrel')
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})

        if self.room.room_state == "guessing":
            if current_time.timestamp() <= self.room.room_deadline_time:
                if "guess" in text_data_json:
                    for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = text_data_json["guess"]["lat"]
                            get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lng"] = text_data_json["guess"]["lng"]
                            break
                    await sync_to_async(self.room.save)(using='nonrel')

            if current_time.timestamp() >= self.room.room_deadline_time and not all(get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] for user in self.room.room_members):
                for user in self.room.room_members:
                        if user["username"] == self.nickname:
                            if not get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"]:
                                get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = 0
                                get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] = 0
            
            if current_time.timestamp() >= self.room.room_deadline_time or all(get_dict_from_list(get_dict_from_list(user["rounds"], "round_number", self.room.room_round)["guessings"], "guess_number", self.room.player_turn)["guess_geopoint"]["lat"] for user in self.room.room_members):
                # move to results phase
                self.room.room_state = "results"
                self.room.room_deadline_time = (current_time + timedelta(seconds=5)).timestamp()
                await sync_to_async(self.room.save)(using='nonrel')
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})
        
        elif self.room.room_state == "results":
            if current_time.timestamp() >= self.room.room_deadline_time:
                if self.room.room_round < self.room.room_configs["number_of_rounds"]:
                    # move to next guessing phase
                    self.room.room_state = "guessing"
                    self.room.room_round = self.room.room_round + 1
                    self.room.room_deadline_time = (current_time + timedelta(seconds=self.room.room_configs["time_per_guess"])).timestamp()
                else:
                    # move to endgame phase
                    self.room.room_state = "endgame"

                await sync_to_async(self.room.save)(using='nonrel')
                await self.channel_layer.group_send(self.room_group_name,{"type": "chat_message", "room": self.room, "current_time": current_time.timestamp()})

    async def chat_message(self, event):
        room = event["room"]
        
        await self.send(text_data=json.dumps({"room": RoomSerializer(room).data, "current_time": event["current_time"]}))