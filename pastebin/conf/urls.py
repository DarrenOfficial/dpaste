from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from piston.resource import Resource
from pastebin.apps.api.handlers import SnippetHandler

admin.autodiscover()
snippet_resource = Resource(handler=SnippetHandler)

urlpatterns = patterns('',
    (r'^', include('pastebin.apps.dpaste.urls')),
    
    # Static
    url(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}, name='about'),
    
    # Bla
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),
    
    # API
    url(r'^api/(?P<secret_id>[^/]+)/$', snippet_resource),
    url(r'^api/$', snippet_resource),
)

urlpatterns += staticfiles_urlpatterns()
