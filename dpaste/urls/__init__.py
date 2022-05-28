from django.urls import include, re_path
from django.conf import settings

url_prefix = getattr(settings, "URL_PREFIX", "")

urlpatterns = [
    re_path(r"^%s" % url_prefix, include("dpaste.urls.dpaste_api")),
    re_path(r"^%s" % url_prefix, include("dpaste.urls.dpaste")),
    re_path(r"^%si18n/" % url_prefix, include("django.conf.urls.i18n")),
]

# Custom error handlers which load `dpaste/<code>.html` instead of `<code>.html`
handler404 = "dpaste.views.handler404"
handler500 = "dpaste.views.handler500"
