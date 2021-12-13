from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from ..views import APIView

urlpatterns = [
    re_path(r"^api/$", csrf_exempt(APIView.as_view()), name="dpaste_api_create_snippet",)
]
