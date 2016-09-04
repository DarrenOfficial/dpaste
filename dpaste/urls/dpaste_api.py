from django.conf.urls import url

from ..views import snippet_api

urlpatterns = [
    url(r'^api/$', snippet_api, name='dpaste_api_create_snippet'),
]
