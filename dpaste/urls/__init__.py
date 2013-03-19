from django.conf.urls.defaults import url, patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}, name='about'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('dpaste.urls.dpaste_api')),
    url(r'^', include('dpaste.urls.dpaste')),
)
