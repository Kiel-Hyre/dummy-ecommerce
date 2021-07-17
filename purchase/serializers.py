from rest_framework import serializers


class ItemSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField()

    def get_id(self, obj):
        return str(obj.uid)

class ItemAddSerializer(serializers.Serializer):
    name = serializers.CharField()