import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


from . import serializers


# from tutorials django-channels
class PurchaseConsumer(WebsocketConsumer):

    # when connecting
    def connect(self):
        self.room_group_name = 'purchase-socket'

        # join room-group use for layer
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data_json = json.loads(text_data)
        action = data_json.pop('action')


        # Send message to room group
        # perform, logic mostly here since if performed in group_send, it will
        # duplicate
        from . import models
        if action == 'submit':
            name = data_json.get('name', '')
            serializer = serializers.ItemAddSerializer(data=data_json)
            if not serializer.is_valid(): return

            obj = models.Item.objects.create(name=name)
            created = serializers.ItemSerializer(obj).data
            created['action'] = 'created'

            # makes it to apply to other, if direct send only on that ind only
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                'type': 'item_add', # function
                'created': created
            })

        if action == 'remove':
            uid = data_json.get('id', None)
            try: models.Item.objects.get(uid=uid).delete()
            except Exception as e: return

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                'type': 'item_remove', # function
                'deleted': {
                    'id': uid,
                    'action': 'deleted'
                }
            })

    # Receive message from room group
    def item_add(self, event):
        self.send(text_data=json.dumps(
            event['created']
        ))

    def item_remove(self, event):
        self.send(text_data=json.dumps(
            event['deleted']
        ))