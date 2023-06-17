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
        (30.3285, 35.4419),     # Wadi Rum, Jordan
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
        (-22.9519, -43.2105),  # Christ the Redeemer (Cristo Redentor), Rio de Janeiro
        (-22.9488, -43.1576),  # Sugarloaf Mountain (Pão de Açúcar), Rio de Janeiro
        (-25.6953, -54.4367),  # Iguazu Falls (Cataratas do Iguaçu), Paraná
        (-22.9739, -43.1856),  # Copacabana Beach, Rio de Janeiro
        (-12.9724, -38.5124),  # Salvador Historic Center (Pelourinho), Salvador
        (-3.8405, -32.4135),   # Fernando de Noronha, Pernambuco
        (-2.5056, -43.1750),   # Lençóis Maranhenses National Park, Maranhão
        (-22.9122, -43.2302),  # Maracanã Stadium, Rio de Janeiro
        (-23.5618, -46.6568),  # Avenida Paulista, São Paulo
        (-15.7998, -47.8827),  # Brasília Cathedral (Catedral Metropolitana de Brasília), Brasília
        (-22.9105, -43.1742),  # Theatro Municipal, Rio de Janeiro
        (-28.1770, -48.6523),  # Praia do Rosa, Santa Catarina
        (-22.9709, -43.3022),  # Tijuca National Park (Parque Nacional da Tijuca), Rio de Janeiro
        (-20.3836, -43.5030),  # Ouro Preto, Minas Gerais
        (-25.4165, -54.5875),  # Itaipu Dam (Usina Hidrelétrica de Itaipu), Paraná
        (-12.9693, -38.5127),  # São Francisco Church and Convent (Igreja e Convento de São Francisco), Salvador
        (-12.6165, -41.4923),   # Chapada Diamantina National Park, Bahia
        (37.8651, -119.5383),  # Yosemite National Park, California
        (37.7749, -122.4194),  # Golden Gate Bridge, San Francisco, California
        (34.0522, -118.2437),  # Hollywood Walk of Fame, Los Angeles, California
        (34.0522, -118.2507),  # Griffith Observatory, Los Angeles, California
        (36.1699, -115.1398),  # Las Vegas Strip, Las Vegas, Nevada
        (40.7589, -73.9851),   # Times Square, New York City, New York
        (38.9072, -77.0369),   # White House, Washington D.C.
        (41.8781, -87.6298),   # Millennium Park, Chicago, Illinois
        (37.7749, -122.4194),  # Alcatraz Island, San Francisco, California
        (38.9072, -123.5083),  # Redwood National and State Parks, California
        (29.9511, -90.0715),   # French Quarter, New Orleans, Louisiana
        (47.6062, -122.3321),  # Pike Place Market, Seattle, Washington
        (40.7128, -74.0060),   # Statue of Liberty, New York City, New York
        (33.7489, -84.3789),   # Centennial Olympic Park, Atlanta, Georgia
        (41.8781, -87.6298),   # Navy Pier, Chicago, Illinois
        (38.9072, -77.0369),   # National Mall, Washington D.C.
        (25.7617, -80.1918),   # South Beach, Miami, Florida
        (41.8919, -87.6089),   # The Art Institute of Chicago, Illinois
        (34.0500, -118.2500),  # Universal Studios Hollywood, Los Angeles, California
        (36.1699, -115.1398),   # Bellagio Hotel and Casino, Las Vegas, Nevada
        (51.1789, -1.8262),    # Stonehenge, Wiltshire, England
        (48.8584, 2.2945),     # Eiffel Tower, Paris, France
        (41.9028, 12.4964),    # Vatican City, Rome, Italy
        (51.1657, 10.4515),    # Neuschwanstein Castle, Bavaria, Germany
        (55.6761, 12.5683),    # Nyhavn, Copenhagen, Denmark
        (40.4319, -3.6893),    # Plaza Mayor, Madrid, Spain
        (48.1351, 11.5820),    # Marienplatz, Munich, Germany
        (41.4036, 2.1744),     # Park Güell, Barcelona, Spain
        (59.3293, 18.0686),    # Gamla Stan (Old Town), Stockholm, Sweden
        (48.8566, 2.3522),     # Notre-Dame Cathedral, Paris, France
        (55.7517, 37.6178),    # Red Square, Moscow, Russia
        (45.4384, 12.3271),    # St. Mark's Square, Venice, Italy
        (52.5163, 13.3779),    # Brandenburg Gate, Berlin, Germany
        (41.9028, 12.4964),    # Trevi Fountain, Rome, Italy
        (47.3769, 8.5417),     # Rhine Falls, Schaffhausen, Switzerland
        (55.6761, 12.5683),    # Tivoli Gardens, Copenhagen, Denmark
        (41.9028, 12.4964),    # Roman Colosseum, Rome, Italy
        (55.7558, 37.6176),    # Bolshoi Theatre, Moscow, Russia
        (51.1657, 10.4515),    # Zugspitze, Bavaria, Germany
        (47.4979, 19.0402),     # Széchenyi Thermal Bath, Budapest, Hungary
        # Japan
        (35.6895, 139.6917),   # Tokyo Tower, Tokyo
        (35.7101, 139.8107),   # Shibuya Crossing, Tokyo
        (34.6937, 135.5023),   # Fushimi Inari Taisha, Kyoto
        (35.0116, 135.7681),   # Kiyomizu-dera, Kyoto
        (35.6762, 139.6503),   # Meiji Shrine, Tokyo
        (35.6895, 139.6917),   # Tokyo Disneyland, Tokyo
        (34.6881, 135.8430),   # Osaka Castle, Osaka
        (34.6863, 135.5259),   # Arashiyama Bamboo Grove, Kyoto
        (35.6895, 139.6917),   # Shinjuku Gyoen National Garden, Tokyo
        (35.6895, 139.6917),   # Akihabara, Tokyo
        # Philippines
        (14.5906, 120.9794),   # Rizal Park, Manila
        (14.5906, 120.9794),   # Intramuros, Manila
        (9.9623, 123.3840),    # Chocolate Hills, Bohol
        (13.4443, 144.7937),   # Tumon Bay, Guam
        (13.1631, 123.7480),   # Mayon Volcano, Albay
        (11.9400, 121.9533),   # Boracay Island, Aklan
        (14.6760, 121.0437),   # Manila Ocean Park, Manila
        (9.2833, 123.4122),    # Kawasan Falls, Cebu
        (10.3157, 123.8854),   # Fort San Pedro, Cebu
        (9.1953, 123.2569),    # Oslob Whale Shark Watching, Cebu
        # South Korea
        (37.5665, 126.9780),   # Gyeongbokgung Palace, Seoul
        (37.5665, 126.9780),   # Myeongdong, Seoul
        (37.5796, 126.9770),   # N Seoul Tower, Seoul
        (33.5185, 126.5288),   # Hyeopjae Beach, Jeju Island
        (37.5665, 126.9780),   # Bukchon Hanok Village, Seoul
        (37.5665, 126.9780),   # Lotte World Tower, Seoul
        (35.1796, 129.0756),   # Haedong Yonggungsa Temple, Busan
        (37.5665, 126.9780),   # Changdeokgung Palace, Seoul
        (37.5123, 127.0512),   # Gangnam District, Seoul
        (35.9078, 127.7669),   # Jeonju Hanok Village, Jeonju
        # Indonesia
        (-8.4095, 115.1889),   # Tanah Lot, Bali
        (-6.1751, 106.8650),   # National Monument (Monas), Jakarta
        (-7.9813, 112.6307),   # Mount Bromo, East Java
        (-8.6500, 115.2167),   # Ubud Monkey Forest, Bali
        (-7.7956, 110.3695),   # Borobudur Temple, Central Java
        (-8.4095, 115.1889),   # Uluwatu Temple, Bali
        (-6.2297, 106.8296),   # Taman Mini Indonesia Indah, Jakarta
        (-8.5833, 116.1167),   # Gili Islands, West Nusa Tenggara
        (-6.1754, 106.8272),   # Istiqlal Mosque, Jakarta
        (-6.1214, 106.7741),    # Jakarta Old Town, Jakarta
        # Singapore
        (1.2894, 103.8592),    # Marina Bay Sands, Singapore
        (1.3521, 103.8198),    # Gardens by the Bay, Singapore
        (1.2821, 103.8506),    # Sentosa Island, Singapore
        (1.2809, 103.8481),    # Universal Studios Singapore
        (1.3000, 103.8431),    # Orchard Road, Singapore
        (1.2897, 103.8501),    # Merlion Park, Singapore
        (1.3196, 103.8434),    # Singapore Botanic Gardens
        (1.2879, 103.8466),    # Clarke Quay, Singapore
        (1.3521, 103.8178),    # ArtScience Museum, Singapore
        (1.2786, 103.8436),     # Raffles Hotel, Singapore
        # Canada
        (51.1784, -115.5708),    # Banff National Park, Alberta
        (45.4215, -75.6981),     # Parliament Hill, Ottawa, Ontario
        (49.2827, -123.1207),    # Stanley Park, Vancouver, British Columbia
        (43.6532, -79.3832),     # CN Tower, Toronto, Ontario
        (45.5017, -73.5673),     # Old Montreal, Montreal, Quebec
        (53.5444, -113.4909),    # West Edmonton Mall, Edmonton, Alberta
        (48.4284, -123.3656),    # Inner Harbour, Victoria, British Columbia
        (48.8588, -123.5152),    # Butchart Gardens, Brentwood Bay, British Columbia
        (45.4215, -75.6981),     # Rideau Canal, Ottawa, Ontario
        (51.0447, -114.0719),    # Calgary Stampede, Calgary, Alberta
        # Mexico
        (19.4326, -99.1332),     # Zócalo, Mexico City
        (21.1619, -86.8515),     # Tulum Ruins, Tulum, Quintana Roo
        (20.6843, -88.5678),     # Chichen Itza, Yucatán
        (25.6866, -100.3161),    # Macroplaza, Monterrey, Nuevo León
        (21.1619, -86.8515),     # Playa del Carmen, Quintana Roo
        (19.0403, -98.2062),     # Puebla Cathedral, Puebla
        (19.4326, -99.1332),     # Frida Kahlo Museum, Mexico City
        (25.5720, -108.4708),    # Copper Canyon, Chihuahua
        (21.1619, -86.8515),     # Xcaret Park, Quintana Roo
        (19.4978, -99.1269),     # Chapultepec Castle, Mexico City
        # Argentina
        (-34.6037, -58.3816),    # Plaza de Mayo, Buenos Aires
        (-41.1335, -71.3103),    # Perito Moreno Glacier, Santa Cruz
        (-24.7829, -65.4122),    # Salinas Grandes, Jujuy
        (-34.6291, -58.4284),    # La Boca, Buenos Aires
        (-31.4155, -64.1835),    # Cordoba Cathedral, Cordoba
        (-34.6037, -58.3816),    # Teatro Colón, Buenos Aires
        (-42.7700, -65.0400),    # Peninsula Valdes, Chubut
        (-41.1317, -71.3102),    # Cerro Catedral, Bariloche, Rio Negro
        (-23.2375, -67.2208),    # Quebrada de Humahuaca, Jujuy
        (-32.9569, -60.6686),     # National Flag Memorial, Rosario, Santa Fe
        # Australia
        (-33.8568, 151.2153),   # Sydney Opera House, Sydney
        (-37.8136, 144.9631),   # Federation Square, Melbourne
        (-27.4698, 153.0251),   # South Bank, Brisbane
        (-31.9505, 115.8605),   # Kings Park, Perth
        (-34.9285, 138.6007),   # Adelaide Oval, Adelaide
        (-33.8679, 151.2093),   # Bondi Beach, Sydney
        (-42.8821, 147.3272),   # Salamanca Market, Hobart
        (-35.2809, 149.1300),   # Australian War Memorial, Canberra
        (-27.4698, 153.0251),   # Lone Pine Koala Sanctuary, Brisbane
        (-12.4634, 130.8456),   # Mindil Beach, Darwin
        # New Zealand
        (-36.8485, 174.7633),   # Sky Tower, Auckland
        (-41.2865, 174.7762),   # Te Papa Tongarewa, Wellington
        (-45.8664, 170.5170),   # Cadbury World, Dunedin
        (-41.2906, 173.2349),   # Marlborough Sounds, Marlborough
        (-36.8530, 174.7630),   # Waiheke Island, Auckland
        (-43.5321, 172.6362),   # Christchurch Botanic Gardens, Christchurch
        (-37.7870, 175.2793),   # Hobbiton Movie Set, Matamata
        (-41.2906, 173.2349),   # Abel Tasman National Park, Nelson
        (-41.2865, 174.7762),   # Oriental Bay, Wellington
        (-45.0312, 168.6626),    # Milford Sound, Southland
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