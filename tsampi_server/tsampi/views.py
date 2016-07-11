from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import json
from collections import namedtuple
from rest_framework.response import Response
from rest_framework import generics
from tsampi import utils
from . import tasks
from . import serializers
from celery.result import AsyncResult
from django.shortcuts import redirect
from cacheback.decorators import cacheback



TsampiApp = namedtuple('TsampiApp', ['app_name'])

class AppList(generics.ListAPIView):
    """
    All available Tsampi Apps
    """
    serializer_class = serializers.AppSerializer

    def get_queryset(self):
        apps = cacheback(10)(utils.list_apps)()
        app_dict =  [TsampiApp(app_name=name) for name in apps]
        return app_dict



class AppDetail(APIView):
    '''List of functions in the Tsampi app

    Call a function with JSONRPC.

        {
            "id": 1,
            "method": "echo",
            "params": ["tim"],
            "jsonrpc": "2.0"
        }
    '''

    def post(self, request, app_name):
        result = tasks.call_tsampi_chain.delay(app_name, json.dumps(request.data))
        response = redirect('task-detail', result.task_id)
        response.status_code = 303
        return response

    def get(self, request, app_name):
        d = cacheback(10)(utils.call_tsampi_chain)(app_name)
        return Response(d)

class TaskDetail(APIView):
    serializer_class = serializers.TaskSerializer

    def get(self, request, task_id):
        # TODO: delete task after sucessfully returned
        r = AsyncResult(task_id)
        return Response(serializers.TaskSerializer(r, context={'request': request}).data)
