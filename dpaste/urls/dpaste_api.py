from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from ..views import APIView

urlpatterns = [
    url(
        r'^api/$',
        csrf_exempt(APIView.as_view()),
        name='dpaste_api_create_snippet',
    )
]
