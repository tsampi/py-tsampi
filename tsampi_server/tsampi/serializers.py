from rest_framework import serializers
from rest_framework.reverse import reverse
import json


class GitUrlSerializer(serializers.Serializer):
    git_url = serializers.URLField()



class AppSerializer(serializers.Serializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='app-detail', lookup_field='app_name')
    app_name = serializers.CharField()


class TaskSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='task-detail', lookup_field='task_id')
    id = serializers.UUIDField(format='hex_verbose')
    state = serializers.CharField()
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        try:
            json.dumps(obj.result)  # Precheck that the result is json serializable
            j = obj.result
        except Exception as e:
            print(e)
            j = str(obj.result)

        return j
