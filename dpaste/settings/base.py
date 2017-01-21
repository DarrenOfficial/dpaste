# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *


#==============================================================================
# Calculation of directories relative to the module location
#==============================================================================
import os
import sys
import dpaste

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(dpaste.__file__))
)

# Set the variable root to $VIRTUALENV/var.
PYTHON_BIN = os.path.dirname(sys.executable)

VAR_ROOT = os.path.join(os.path.dirname(PYTHON_BIN), 'var')
if not os.path.exists(VAR_ROOT):
    os.mkdir(VAR_ROOT)

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'UTC'
SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

ALLOWED_HOSTS = (
    'dpaste.de',
    'www.dpaste.de',
    'dpaste.org',
    'www.dpaste.org',
    '127.0.0.1',
)

SECRET_KEY = 'CHANGE_ME'

#==============================================================================
# I18N
#==============================================================================

USE_I18N = True
USE_L10N = False

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
    ('de', 'German'),
    ('es', 'Spanish'),
    ('pt-br', 'Portugese (Brasil)'),
)

LOCALE_PATHS = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locale')),
)

#==============================================================================
# Static files
#==============================================================================

STATIC_ROOT = os.path.join(VAR_ROOT, 'static')

#==============================================================================
# Project URLS and media settings
#==============================================================================

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

ROOT_URLCONF = 'dpaste.urls'

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

#==============================================================================
# Templates
#==============================================================================

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


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
                'dpaste.context_processors.dpaste_globals',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'gunicorn',
    'dpaste',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
        'USER': '',
        'PASSWORD': '',
    }
}

#==============================================================================
# App specific settings
#==============================================================================

# How many recent snippets to save for every user? IDs of this snippets are
# stored in the user session.
MAX_SNIPPETS_PER_USER = 25

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
