from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/purchase/(?P<room_name>\w+)/$', consumers.PurchaseConsumer.as_asgi()),
]