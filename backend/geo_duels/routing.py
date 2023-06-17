from django.urls import re_path, path

from geo_duels import consumers

websocket_urlpatterns = [
    re_path(r"ws/room/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/spmatch/(?P<room_name>\w+)/$", consumers.SinglePlayerMatchConsumer.as_asgi()),
]