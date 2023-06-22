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
        # World Attractions
        (40.6940675,-74.0529048),   # Statue of Liberty, New York City, USA
        (48.8611784,2.2963307),     # Eiffel Tower, Paris, France
        (27.1738754,78.0428079),    # Taj Mahal, Agra, India
        (-33.8587411,151.2148142),  # Sydney Opera House, Sydney, Australia
        (-22.9451806,-43.1967596),  # Christ the Redeemer, Rio de Janeiro, Brazil
        (-13.1631092,-72.5449208),  # Machu Picchu, Cusco Region, Peru
        (41.8911657,12.4921193),    # Colosseum, Rome, Italy
        (29.9797683,31.1327971),    # Great Pyramid of Giza, Egypt
        (30.3293943,35.4417831),    # Petra, Jordan
        (37.9729837,23.7268789),    # Acropolis of Athens, Greece
        (27.9635027,86.8198438),    # Mount Everest, Nepal/China Border
        (13.4132414,103.8670566),   # Angkor Wat, Siem Reap, Cambodia
        (43.0831627,-79.0756546),   # Niagara Falls, Ontario, Canada/New York, USA
        (51.1788618,-1.8267175),    # Stonehenge, Wiltshire, England
        (19.432573,-99.1330643),   # Teotihuacan, Mexico
        (51.5008596,-0.1255044),    # Buckingham Palace, London, England
        (48.8561379,2.352197),     # Notre-Dame Cathedral, Paris, France
        (27.1744385,78.0421149),    # Agra Fort, Agra, India
        (35.7100222,139.8104795),   # Tokyo Tower, Tokyo, Japan
        (48.8582247,2.2941902),     # Palace of Versailles, Versailles, France
        (55.7516094,37.6178805),    # Red Square, Moscow, Russia
        (30.3286998,35.4422388),     # Wadi Rum, Jordan
        # Random
        (-12.9773614,-38.5045154), # Salvador, Brazil
        (38.6923837,-9.2160112), # Lisbon, Portugal
        (50.3870336,30.4573609), # Kiev, Ukraine
        (35.6821819,139.7620848), # Tokyo, Japan
        (24.0986245,120.6337057), # Taichung, Taiwan
        (4.0303907,121.9772066), # Manila, Philippines
        (8.4062518,8.363645), # Abuja, Nigeria
        (35.6071651,-105.2171809), # Santa Fe, New Mexico, USA
        (47.6030444,-122.3331972), # Seattle, Washington, USA
        (42.7735255,-106.4613534), # Casper, Wyoming, USA
        (52.3139014,18.2261667), # Lodz, Poland
        (52.4384117,4.816337), # Amsterdam, Netherlands
        (53.010169,18.6045554), # Bydgoszcz, Poland
        (-26.9157581,-48.6650539), # Itajai, Brazil
        (-26.9713048,-48.6322289), # Balneario Camboriu, Brazil
        (-27.0216238,-48.6520151), # Camboriu, Brazil
        (-27.1307656,-48.6001424), # Itapema, Brazil
        (-27.5975216,-48.566637), # Bombinhas, Brazil
        (39.7401557,-104.9860203), # Denver, Colorado, USA
        (50.0753735,14.4135662), # Prague, Czech Republic
        (48.2043261,16.3677289), # Vienna, Austria
        (48.7199265,21.2562986), # Kosice, Slovakia
        (41.0058175,28.9761401), # Istanbul, Turkey
        (41.0256005,28.9743368), # Istanbul, Turkey
        (36.4250886,25.4292034), # Santorini, Greece
        (44.4275424,26.0923933), # Bucharest, Romania
        (44.8125289,20.4613769), # Belgrade, Serbia
        (38.0774772,13.4933311), # Palermo, Italy
        (-30.0689807,-51.2375679), # Porto Alegre, Brazil
        (32.7769879,-96.7999747), # Dallas, Texas, USA
        (32.5378216,-117.081405), # Tijuana, Mexico
        (-33.9250877,18.4239157), # Cape Town, South Africa
        (25.1987398,55.2720745), # Dubai, United Arab Emirates
        (63.5433592,-19.6743041), # Reykjavik, Iceland
        (-27.2956298,-70.4942161), # La Serena, Chile
        (28.4779114,77.0426084), # New Delhi, India
        (22.3172115,114.1592772), # Hong Kong, China
        # Brazil
        (-25.6956923,-54.4372682),  # Iguazu Falls (Cataratas do Iguaçu), Paraná
        (-22.9735653,-43.1858853),  # Copacabana Beach, Rio de Janeiro
        (-12.9718112,-38.5148679),  # Salvador Historic Center (Pelourinho), Salvador
        (-3.8407897,-32.4136208),   # Fernando de Noronha, Pernambuco
        (-2.4979008,-43.1963583),   # Lençóis Maranhenses National Park, Maranhão
        (-22.9121536,-43.2301913),  # Maracanã Stadium, Rio de Janeiro
        (-23.560797,-46.6573335),  # Avenida Paulista, São Paulo
        (-15.8000808,-47.8824894),  # Brasília Cathedral (Catedral Metropolitana de Brasília), Brasília
        (-28.1757734,-48.663639),  # Praia do Rosa, Santa Catarina
        (-20.3837184,-43.5029371),  # Ouro Preto, Minas Gerais
        (-25.4148762,-54.5885835),  # Itaipu Dam (Usina Hidrelétrica de Itaipu), Paraná
        # United States
        (37.8326174,-119.4909159),  # Yosemite National Park, California
        (37.7915907,-122.3855299),  # Golden Gate Bridge, San Francisco, California
        (36.1699874,-115.1401008),  # Las Vegas Strip, Las Vegas, Nevada
        (40.7588258,-73.9849384),   # Times Square, New York City, New York
        (38.900249,-77.0364317),   # White House, Washington D.C.
        (41.8755883,-87.6454417),   # Millennium Park, Chicago, Illinois
        (29.9546917,-90.0691064),   # French Quarter, New Orleans, Louisiana
        (47.6067702,-122.3320629),  # Pike Place Market, Seattle, Washington
        (33.7604435,-84.3933626),   # Centennial Olympic Park, Atlanta, Georgia
        (25.7906364,-80.1300947),   # South Beach, Miami, Florida
        (41.9078173,-87.6273142),   # The Art Institute of Chicago, Illinois
        (34.1373948,-118.3558077),  # Universal Studios Hollywood, Los Angeles, California
        # Europe
        (41.9021519,12.4585805),    # Vatican City, Rome, Italy
        (55.6799444,12.5908594),    # Nyhavn, Copenhagen, Denmark
        (40.4156673,-3.707267),    # Plaza Mayor, Madrid, Spain
        (48.1391123,11.5728983),    # Marienplatz, Munich, Germany
        (41.4136045,2.1534422),     # Park Güell, Barcelona, Spain
        (59.3291284,18.0688732),    # Gamla Stan (Old Town), Stockholm, Sweden
        (45.4342372,12.3381749),    # St. Mark's Square, Venice, Italy
        (52.5146269,13.3783465),    # Brandenburg Gate, Berlin, Germany
        (47.6768417,8.6147824),     # Rhine Falls, Schaffhausen, Switzerland
        (55.759558,37.618903),    # Bolshoi Theatre, Moscow, Russia
        (47.5190596,19.0816504),     # Széchenyi Thermal Bath, Budapest, Hungary
        # Japan
        (35.6592632,139.7451773),   # Tokyo Tower, Tokyo
        (34.694346,135.5029972),   # Fushimi Inari Taisha, Kyoto
        (34.99493,135.7852785),   # Kiyomizu-dera, Kyoto
        (35.0222315,135.9515461),   # Meiji Shrine, Tokyo
        (35.6351217,139.8836837),   # Tokyo Disneyland, Tokyo
        (34.6867033,135.5259441),   # Osaka Castle, Osaka
        (35.0167328,135.6702031),   # Arashiyama Bamboo Grove, Kyoto
        (35.6854887,139.7097408),   # Shinjuku Gyoen National Garden, Tokyo
        # Philippines
        (14.5818434,120.9775311),   # Rizal Park, Manila
        # South Korea
        (37.5798091,126.9770773),   # Gyeongbokgung Palace, Seoul
        (33.3943885,126.2388354),   # Hyeopjae Beach, Jeju Island
        (37.5814594,126.9849121),   # Bukchon Hanok Village, Seoul
        (37.5117663,127.1015046),   # Lotte World Tower, Seoul
        (35.1896397,129.2208494),   # Haedong Yonggungsa Temple, Busan
        (37.501648,127.072299),   # Gangnam District, Seoul
        (35.8147099,127.1525936),   # Jeonju Hanok Village, Jeonju
        # Indonesia
        (-8.6209798,115.0872464),   # Tanah Lot, Bali
        (-6.1747144,106.8269666),   # National Monument (Monas), Jakarta
        (-7.9210411,112.9633616),   # Mount Bromo, East Java
        (-8.5192373,115.260865),   # Ubud Monkey Forest, Bali
        (-8.5577103,115.2564031),   # Borobudur Temple, Central Java
        (-8.3475352,116.0513871),   # Gili Islands, West Nusa Tenggara
        # Singapore
        (1.2835405,103.8582378),    # Marina Bay Sands, Singapore
        (1.2809862,103.8632146),    # Gardens by the Bay, Singapore
        (1.2865824,103.8591637),    # ArtScience Museum, Singapore
        # Canada
        (51.5096559,-116.0680336),    # Banff National Park, Alberta
        (45.422561,-75.7002561),     # Parliament Hill, Ottawa, Ontario
        (49.2974065,-123.135964),    # Stanley Park, Vancouver, British Columbia
        (43.639905,-79.3855381),     # CN Tower, Toronto, Ontario
        (45.5038151,-73.5438791),     # Old Montreal, Montreal, Quebec
        (53.5227613,-113.6154822),    # West Edmonton Mall, Edmonton, Alberta
        (48.4208584,-123.3692479),    # Inner Harbour, Victoria, British Columbia
        (45.3959762,-75.6884821),     # Rideau Canal, Ottawa, Ontario
        (51.0364333,-114.0522676),    # Calgary Stampede, Calgary, Alberta
        # Mexico
        (19.4336309,-99.1336609),     # Zócalo, Mexico City
        (20.2149118,-87.4292651),     # Tulum Ruins, Tulum, Quintana Roo
        (20.6796071,-88.5682961),     # Chichen Itza, Yucatán
        (25.6684189,-100.3105522),    # Macroplaza, Monterrey, Nuevo León
        (20.6451107,-87.0550637),     # Playa del Carmen, Quintana Roo
        (19.0432964,-98.1983079),     # Puebla Cathedral, Puebla
        (27.5105009,-107.82168),    # Copper Canyon, Chihuahua
        (20.5804179,-87.1211451),     # Xcaret Park, Quintana Roo
        (19.4206197,-99.1813736),     # Chapultepec Castle, Mexico City
        # Argentina
        (-34.6083538,-58.3725346),    # Plaza de Mayo, Buenos Aires
        (-50.4728324,-73.0326948),    # Perito Moreno Glacier, Santa Cruz
        (-34.6498318,-58.3676939),    # La Boca, Buenos Aires
        (-34.614712,-58.4229039),    # Cordoba Cathedral, Cordoba
        (-34.6011333,-58.3839226),    # Teatro Colón, Buenos Aires
        (-41.1326459,-71.3104679),    # Cerro Catedral, Bariloche, Rio Negro
        (-23.1112722,-65.3722421),    # Quebrada de Humahuaca, Jujuy
        (-32.9478321,-60.6299122),     # National Flag Memorial, Rosario, Santa Fe
        # Australia
        (-33.8561435,151.2154923),   # Sydney Opera House, Sydney
        (-37.8178936,144.9689882),   # Federation Square, Melbourne
        (-27.4776396,153.0231596),   # South Bank, Brisbane
        (-34.9153151,138.5954088),   # Adelaide Oval, Adelaide
        (-33.891194,151.2759991),   # Bondi Beach, Sydney
        # New Zealand
        (-36.8481302,174.7623019),   # Sky Tower, Auckland
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