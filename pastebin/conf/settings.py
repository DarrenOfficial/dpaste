# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'UTC'
SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

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
import pastebin

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(pastebin.__file__))
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

ROOT_URLCONF = 'pastebin.conf.urls'

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

#==============================================================================
# Templates
#==============================================================================

MIDDLEWARE_CLASSES = (
    'pastebin.disable.DisableCSRF',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'mptt',
    'south',
    'pastebin',
    'pastebin.apps.dpaste',
    'gunicorn',
    'raven.contrib.django',
)

#==============================================================================
# App specific settings
#==============================================================================

# How many recent snippets to save for every user? IDs of this snippets are
# stored in the user session.
MAX_SNIPPETS_PER_USER = 25

SENTRY_DSN = 'http://0afbf6df0a9749f9985059ed6c527b19:717d9800ba854149a7e7f6a501b2caa0@ohnoez.mahner.org/2'