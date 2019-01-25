# Import global settings to make it easier to extend settings.
# ==============================================================================
# Calculation of directories relative to the module location
# ==============================================================================
import os
import sys

from django.conf.global_settings import *

import dpaste

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(dpaste.__file__))
)

PYTHON_BIN = os.path.dirname(sys.executable)
if os.path.exists(os.path.join(PYTHON_BIN, 'activate_this.py')):
    # Assume that the presence of 'activate_this.py' in the python bin/
    # directory means that we're running in a virtual environment. Set the
    # variable root to $VIRTUALENV/var.
    VAR_ROOT = os.path.join(os.path.dirname(PYTHON_BIN), 'var')
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
else:
    # Set the variable root to the local configuration location (which is
    # ignored by the repository).
    VAR_ROOT = os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'conf', 'local')

# ==============================================================================
# Generic Django project settings
# ==============================================================================

DEBUG = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'UTC'
SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

ALLOWED_HOSTS = ['*']

# ==============================================================================
# I18N
# ==============================================================================

USE_I18N = True
USE_L10N = False

LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'),)

# LOCALE_PATHS = (
#     os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locale')),
# )

# ==============================================================================
# Project URLS and media settings
# ==============================================================================

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
)

STATICFILES_DIRS = (os.path.join(PROJECT_DIR, 'build'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = os.path.join(VAR_ROOT, 'static')

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

ROOT_URLCONF = 'dpaste.urls'

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

# ==============================================================================
# Templates
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
            ]
        },
    }
]

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'staticinline.apps.StaticInlineAppConfig',
    'dpaste.apps.dpasteAppConfig',
]

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'dev.db',
#         'USER': '',
#         'PASSWORD': '',
#     }
# }

# ==============================================================================
# App specific settings
# ==============================================================================

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    },
}
