from rest_framework import serializers


class AppSerializer(serializers.Serializer):

    def to_representation(self, data):
        return {'data': data}

