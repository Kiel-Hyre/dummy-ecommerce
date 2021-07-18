import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async as db_syn_asyn

from . import models, serializers


# from tutorials django-channels
class PurchaseConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.receive_methods_dict = {
            'submit': self.item_add,
            'remove': self. item_remove,
        }

    # when connecting, prefer not do list objects here rather through api or
    # direct render, if ws had reconnecting option it will lead to duplication
    async def connect(self):
        self.room_group_name = 'purchase-socket'

        # join room-group use for layer
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        action = data_json.pop('action', None)

        func = self.receive_methods_dict.get(action, None)
        if not func: return
        await func(data_json)

    async def item_add(self, data_json, *args, **kwargs):
        serializer = serializers.ItemAddSerializer(data=data_json)
        if not serializer.is_valid(): return

        obj = await db_syn_asyn(self.create_item)(name=data_json.get('name', ''))
        created = serializers.ItemSerializer(obj).data
        created['action'] = 'created'

        # makes it to apply to other, if direct send only on that ind only
        await self.channel_layer.group_send(
            self.room_group_name,{
            'type': 'sub_item_add', # function
            'created': created })

    async def item_remove(self, data_json, *args, **kwargs):
        uid = data_json.get('id', None)
        if not await db_syn_asyn(self.delete_item)(uid=uid): return
        await self.channel_layer.group_send(
            self.room_group_name,{
            'type': 'sub_item_remove', # function
            'deleted': { 'id': uid, 'action': 'deleted'}
        })

    # Receive message from room group
    async def sub_item_add(self, event):
        await self.send(text_data=json.dumps(event['created']))

    async def sub_item_remove(self, event):
        await self.send(text_data=json.dumps(event['deleted']))

    # db queries, can do in manager
    def create_item(self, *args, **kwargs):
        return models.Item.objects.create(**kwargs)

    def delete_item(self, *args, **kwargs):
        try:return models.Item.objects.filter(**kwargs).delete()
        except: return False