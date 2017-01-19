from django.conf import settings
from django.conf.urls import url

from .. import views

L = getattr(settings, 'DPASTE_SLUG_LENGTH', 4)

urlpatterns = [
    url(r'^about/$', views.about, name='dpaste_about'),

    url(r'^$', views.snippet_new, name='snippet_new'),
    url(r'^diff/$', views.snippet_diff, name='snippet_diff'),
    url(r'^history/$', views.snippet_history, name='snippet_history'),
    url(r'^delete/$', views.snippet_delete, name='snippet_delete'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/?$' % L, views.snippet_details, name='snippet_details'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/delete/$' % L, views.snippet_delete, name='snippet_delete'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]{%d,})/raw/?$' % L, views.snippet_details, {'template_name': 'dpaste/snippet_details_raw.html', 'is_raw': True}, name='snippet_details_raw'),
]
