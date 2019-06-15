from django.apps import apps
from django.conf import settings
from django.conf.urls import url
from django.views.decorators.cache import cache_control
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView
from django.conf.urls.static import static
#from django.contrib.staticfiles import views as static_views

from .. import views
from .. import contribute

L = getattr(settings, "DPASTE_SLUG_LENGTH", 4)
config = apps.get_app_config("dpaste")

urlpatterns = [
    url(r'^$', views.SnippetView.as_view(), name='snippet_new'),
    #url(
    #    r'^static/(?P<path>.*)$',
    #    static_views.serve,
    #),
    url(
        r"^about/$",
        cache_control(max_age=config.CACHE_TIMEOUT)(
            TemplateView.as_view(
                template_name="dpaste/about.html",
                extra_context=config.extra_template_context,
            )
        ),
        name="dpaste_about",
    ),
    url(r"^history/$", views.SnippetHistory.as_view(), name="snippet_history"),
    url(
        r"^(?P<snippet_id>[a-zA-Z0-9]{%d,})/?$" % L,
        views.SnippetDetailView.as_view(),
        name="snippet_details",
    ),
    url(
        r"^(?P<snippet_id>[a-zA-Z0-9]{%d,})/raw/?$" % L,
        views.SnippetRawView.as_view(),
        name="snippet_details_raw",
    ),
    url(
        r"^(?P<snippet_id>[a-zA-Z0-9]{%d,})/slim/?$" % L,
        xframe_options_exempt(
            views.SnippetDetailView.as_view(template_name="dpaste/details_slim.html")
        ),
        name="snippet_details_slim",
    ),
    url(
        r'^contribute.json$',
        contribute.contrib_file,
        name='contrib_file',
    ),
]
