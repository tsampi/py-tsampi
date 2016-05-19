from django.conf.urls import url, include
from tsampi.views import AppList, AppDetail


urlpatterns = [
    url(r'^apps/$', AppList.as_view(), name='app-list'),
    url(r'^apps/(?P<app_name>[a-zA-Z0-9_-]+)/$', AppDetail.as_view(), name='app-detail'),

]
