from django.urls import include, re_path

urlpatterns = [
    re_path(r"^", include("dpaste.urls.dpaste_api")),
    re_path(r"^", include("dpaste.urls.dpaste")),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
]

# Custom error handlers which load `dpaste/<code>.html` instead of `<code>.html`
handler404 = "dpaste.views.handler404"
handler500 = "dpaste.views.handler500"
