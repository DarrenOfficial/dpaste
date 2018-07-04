from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView

from .. import views

L = getattr(settings, 'DPASTE_SLUG_LENGTH', 4)

urlpatterns = [
    url(r'^$', views.SnippetView.as_view(), name='snippet_new'),
    url(
        r'^about/$',
        TemplateView.as_view(template_name='dpaste/about.html'),
        name='dpaste_about',
    ),
    url(r'^history/$', views.SnippetHistory.as_view(), name='snippet_history'),
    url(
        r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/?$' % L,
        views.SnippetDetailView.as_view(),
        name='snippet_details',
    ),
    url(
        r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/raw/?$' % L,
        views.SnippetRawView.as_view(),
        name='snippet_details_raw',
    ),
]
