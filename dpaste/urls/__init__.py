from django.conf.urls.defaults import url, patterns, include
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^about/$', TemplateView.as_view(template_name='dpaste/about.html'), name='about'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('dpaste.urls.dpaste_api')),
    url(r'^', include('dpaste.urls.dpaste')),
)

# Custom error handlers which load `dpaste/<code>.html` instead of `<code>.html`
handler404 = 'dpaste.views.page_not_found'
handler500 = 'dpaste.views.server_error'