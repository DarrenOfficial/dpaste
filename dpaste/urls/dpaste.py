from django.apps import apps
from django.conf import settings
from django.urls import re_path
from django.views.decorators.cache import cache_control
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView

from .. import views

L = getattr(settings, "DPASTE_SLUG_LENGTH", 4)
config = apps.get_app_config("dpaste")

urlpatterns = [
    re_path(r"^$", views.SnippetView.as_view(), name="snippet_new"),
    re_path(
        r"^about/$",
        cache_control(max_age=config.CACHE_TIMEOUT)(
            TemplateView.as_view(
                template_name="dpaste/about.html",
                extra_context=config.extra_template_context,
            )
        ),
        name="dpaste_about",
    ),
    re_path(r"^history/$", views.SnippetHistory.as_view(), name="snippet_history"),
    re_path(
        r"^(?P<snippet_id>[a-zA-Z0-9]{%d,})/?$" % L,
        views.SnippetDetailView.as_view(),
        name="snippet_details",
    ),
    re_path(
        r"^(?P<snippet_id>[a-zA-Z0-9]{%d,})/raw/?$" % L,
        views.SnippetRawView.as_view(),
        name="snippet_details_raw",
    ),
    re_path(
        r"^(?P<snippet_id>[a-zA-Z0-9]{%d,})/slim/?$" % L,
        xframe_options_exempt(
            views.SnippetDetailView.as_view(template_name="dpaste/details_slim.html")
        ),
        name="snippet_details_slim",
    ),
]
