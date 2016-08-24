from django.conf.urls import url, include
from tsampi.views import AppList, AppDetail, TaskDetail, index_view, PullView
from django.views.decorators.cache import never_cache


urlpatterns = [
    url(r'^$', index_view, name='index-view'),
    url(r'^pull/$', PullView.as_view(), name='pull-view'),
    url(r'^task/(?P<task_id>[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})/$',
        TaskDetail.as_view(), name='task-detail'),
    url(r'^apps/$', AppList.as_view(), name='app-list'),
    url(r'^apps/(?P<app_name>[a-zA-Z0-9_-]+)/$',
        AppDetail.as_view(), name='app-detail'),

]
