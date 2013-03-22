from django.conf.urls.defaults import url, patterns, include
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^about/$', 'dpaste.views.about', name='about'),
    url(r'^', include('dpaste.urls.dpaste_api')),
    url(r'^', include('dpaste.urls.dpaste')),
)

# Custom error handlers which load `dpaste/<code>.html` instead of `<code>.html`
handler404 = 'dpaste.views.page_not_found'
handler500 = 'dpaste.views.server_error'