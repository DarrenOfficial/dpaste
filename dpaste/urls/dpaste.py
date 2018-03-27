from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url

from .. import views

L = getattr(settings, 'DPASTE_SLUG_LENGTH', 4)

urlpatterns = [
    url(r'^$', views.SnippetView.as_view(), name='snippet_new'),
    url(r'^about/$', views.AboutView.as_view(), name='dpaste_about'),
    url(r'^history/$', views.SnippetHistory.as_view(), name='snippet_history'),

    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/?$' % L,
        views.SnippetDetailView.as_view(), name='snippet_details'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/raw/?$' % L,
        views.SnippetRawView.as_view(), name='snippet_details_raw'),
]
