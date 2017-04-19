from rest_framework import serializers
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


class ResultSerializer(serializers.Serializer):
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


def make_printable(obj):
    if isinstance(obj, dict):
        return {make_printable(k): make_printable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_printable(elem) for elem in obj]
    elif isinstance(obj, str):
        # Only printables
        return ''.join(x for x in obj if x in string.printable)
    else:
        return obj


class JSONSerializerMixin:

    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception as e:
                raise serializers.ValidationError(str(e))

        return make_printable(data)

    def to_representation(self, value):
        class JSONish(type(value)):

            """
            Helper class to properly render JSON in the HTML form.
            Without this it will either put the JSON as a string in the json response
            or it will put a pyhton dict as a string in html and json renders
            """

            def __str__(self):
                return json.dumps(self, sort_keys=True)

        return JSONish(value)


class JSONSerializer(JSONSerializerMixin, serializers.Serializer):
    pass


class JSONSerializerField(JSONSerializerMixin, serializers.CharField):
    pass
