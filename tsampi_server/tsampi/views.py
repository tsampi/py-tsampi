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
from django.contrib.sites.shortcuts import get_current_site
from cacheback.decorators import cacheback
from django.conf import settings
from django.http import HttpResponse
import git


# don't need a django model, and a full class is still overkill
TsampiApp = namedtuple('TsampiApp', ['app_name'])


def index_view(request):
    html = '''<pre> _______                        _
 |__   __|                      (_)
    | |___  __ _ _ __ ___  _ __  _
    | / __|/ _` | '_ ` _ \| '_ \| |
    | \__ \ (_| | | | | | | |_) | |
    |_|___/\__,_|_| |_| |_| .__/|_|
                          | |
                          |_|

commit: {commit}
version: {api}</pre>'''.format(**settings.TSAMPI_VERSION)
    return HttpResponse(html)

class PullView(APIView):
    serializer_class = serializers.GitUrlSerializer

    def get(self, request):
        return Response('submit a git url')

    def post(self, request):
        result = tasks.merge_from_peer.delay(settings.TSAMPI_CHAIN, request.data['git_url'], push=True, key=settings.TSAMPI_GPG_FINGERPRINT)
        response = redirect('task-detail', result.task_id)
        response.status_code = 303
        return response


class AppList(generics.ListAPIView):
    """
    All available Tsampi Apps
    """
    serializer_class = serializers.AppSerializer

    def get_queryset(self):
        result = cacheback(10)(tasks.call_tsampi_chain)(settings.TSAMPI_CHAIN)
        app_dict = [TsampiApp(app_name=name)
                    for name in result['rpc_response']]
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
        domain = get_current_site(request)
        user=request.user.username
        result = tasks.call_tsampi_chain.delay(
            settings.TSAMPI_CHAIN, app_name, request.data, commit=True, push=True, user=user, email="%s@%s" % (user, domain))
        response = redirect('result-detail', result.task_id)
        response.status_code = 303
        return response

    def get(self, request, app_name):
        d = cacheback(10)(tasks.call_tsampi_chain)(
            settings.TSAMPI_CHAIN, app_name, user=request.user, email="{}@{}".format(user.username, )
        return Response(d['rpc_response'])


class TaskDetail(APIView):
    def get(self, request, task_id):
        # TODO: delete task after sucessfully returned
        r = AsyncResult(task_id)
        r.get()
        data = serializers.TaskSerializer(r, context={'request': request}).data
        return Response(data)


class ResultDetail(APIView):
    def get(self, request, task_id):
        # TODO: delete task after sucessfully returned
        r = AsyncResult(task_id)
        r.get()
        try:
            data = r.result['rpc_response']['result']
        except (KeyError, TypeError) as e:
            data = r.result
        return Response(data)
