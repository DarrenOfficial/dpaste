from dpaste.settings.base import *
import os

DEBUG = False

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
        (3600 * 24 * 7, _('Expire in one week')),
        (3600 * 24 * 24, _('Expire in 21 days')),
    )
    EXPIRE_DEFAULT = 3600


INSTALLED_APPS.remove('dpaste.apps.dpasteAppConfig')
INSTALLED_APPS.append('dpaste.settings.local.ProductionDpasteAppConfig')


