from rest_framework import serializers
from rest_framework.reverse import reverse
import json

class AppSerializer(serializers.Serializer):

    url = serializers.HyperlinkedIdentityField(view_name='app-detail', lookup_field='app_name')
    app_name = serializers.CharField()


class TaskSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='task-detail', lookup_field='task_id')
    id = serializers.UUIDField(format='hex_verbose')
    state = serializers.CharField()
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        try:
            j = json.loads(obj.result)
        except Exception as e:
            print(e)
            j = obj.result

        return j

