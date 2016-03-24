from django.conf import settings
from django.conf.urls import url

from .. import views

L = getattr(settings, 'DPASTE_SLUG_LENGTH', 4)

urlpatterns = [
    url(r'^about/$', views.AboutView.as_view(), name='dpaste_about'),

    url(r'^$', views.SnippetView.as_view(), name='snippet_new'),
    url(r'^diff/$', views.SnippetDiffView.as_view(), name='snippet_diff'),
    url(r'^history/$', views.SnippetHistory.as_view(), name='snippet_history'),
    url(r'^delete/$', views.SnippetDeleteView.as_view(), name='snippet_delete'),

    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/?$' % L, views.SnippetDetailView.as_view(), name='snippet_details'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/delete/$' % L, views.SnippetDeleteView.as_view(), name='snippet_delete'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/gist/$' % L, views.snippet_gist, name='snippet_gist'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/raw/?$' % L, views.SnippetRawView.as_view(), name='snippet_details_raw'),
]
