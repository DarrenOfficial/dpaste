# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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

USE_I18N = False
USE_L10N = False

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
)

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
# Static files
#==============================================================================

STATIC_ROOT = os.path.join(VAR_ROOT, 'static')

#==============================================================================
# Project URLS and media settings
#==============================================================================

MEDIA_URL = '/uploads/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

ROOT_URLCONF = 'dpaste.urls'

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

#==============================================================================
# Templates
#==============================================================================

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.sessions',

    'mptt',
    'south',
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
