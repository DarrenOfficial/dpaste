from dpaste.settings.base import *
import os

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME','dpaste'),
        'USER': os.environ.get('DB_USER','dpaste'),
        'PASSWORD': os.environ.get('DB_PASS','dpaste'),
        'HOST': os.environ.get('DB_HOST','dpaste'),
        'PORT': os.environ.get('DB_PORT',3306),
    }
}

SECRET_KEY = os.environ.get('SESSION_KEY','changeme')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += ('sslserver',)

# Optionally run the runserver as `manage.py runsslserver` to locally
# test correct cookie and csp behavior.
if not 'runsslserver' in sys.argv:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

#
# Uncomment the block below to use a custom AppConfig.
#

from dpaste.apps import dpasteAppConfig
from django.utils.translation import ugettext_lazy as _
#
class ProductionDpasteAppConfig(dpasteAppConfig):
    SLUG_LENGTH = 8
    LEXER_DEFAULT = 'js'
    EXPIRE_CHOICES = (
        ('onetime', _(u'One Time Snippet')),
        (3600, _(u'Expire in one hour')),
        (3600 * 24, _('Expire in one day')),
    )
    EXPIRE_DEFAULT = 3600

INSTALLED_APPS.remove('dpaste.apps.dpasteAppConfig')
INSTALLED_APPS.append('dpaste.settings.local.ProductionDpasteAppConfig')


