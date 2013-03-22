from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from ..handlers import SnippetHandler

snippet_resource = Resource(handler=SnippetHandler)

urlpatterns = patterns('',
    url(r'^api/$', snippet_resource, name='dpaste_api_create_snippet'),
)