from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from ..handlers import SnippetHandler

snippet_resource = Resource(handler=SnippetHandler)

urlpatterns = patterns('',
    url(r'^api/(?P<secret_id>[^/]+)/$', snippet_resource),
    url(r'^api/$', snippet_resource),
)