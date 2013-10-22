from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('dpaste.views',
    url(r'^$', 'snippet_new', name='snippet_new'),
    url(r'^diff/$', 'snippet_diff', name='snippet_diff'),
    url(r'^history/$', 'snippet_history', name='snippet_history'),
    url(r'^delete/$', 'snippet_delete', name='snippet_delete'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]+)/?$', 'snippet_details', name='snippet_details'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]+)/delete/$', 'snippet_delete', name='snippet_delete'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]+)/gist/$', 'snippet_gist', name='snippet_gist'),
    url(r'^(?P<snippet_id>[a-zA-Z0-9]+)/raw/?$', 'snippet_details', {'template_name': 'dpaste/snippet_details_raw.html', 'is_raw': True}, name='snippet_details_raw'),
)
