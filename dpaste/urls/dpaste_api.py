from django.conf.urls import url, patterns
from ..views import snippet_api

urlpatterns = patterns('',
    url(r'^api/$', snippet_api, name='dpaste_api_create_snippet'),
)
