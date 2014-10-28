from django.conf.urls import url, patterns, include

urlpatterns = patterns(
    '',
    url(r'^', include('dpaste.urls.dpaste_api')),
    url(r'^', include('dpaste.urls.dpaste')),

    (r'^i18n/', include('django.conf.urls.i18n')),
)

# Custom error handlers which load `dpaste/<code>.html` instead of `<code>.html`
handler404 = 'dpaste.views.page_not_found'
handler500 = 'dpaste.views.server_error'
