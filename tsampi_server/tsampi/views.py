from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import json

from rest_framework.response import Response
from . import utils
from . import serializers

class AppList(APIView):
    """
    All available Tsampi Apps
    """

    def get(self, request, format=None):
        apps = utils.list_apps()
        return Response(apps)

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
        d = utils.call_tsampi_chain(app_name, json.dumps(request.data))
        return Response(d)

    def get(self, request, app_name):
        d = utils.call_tsampi_chain(app_name)
        return Response(d)


