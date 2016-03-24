from django.conf.urls import patterns, url

from ..views import APIView

urlpatterns = [
    url(r'^api/$', APIView.as_view(), name='dpaste_api_create_snippet'),
]
