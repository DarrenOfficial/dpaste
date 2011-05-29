from django.conf.urls.defaults import *
from django.conf import settings

CONF_MODULE = '%s.conf' % settings.PROJECT_MODULE_NAME

urlpatterns = patterns('',
    (r'', include('%s.urls' % CONF_MODULE)),
    (r'', include('%s.common.urls.admin' % CONF_MODULE)),
)
