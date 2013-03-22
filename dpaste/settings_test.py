from dpaste.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
        'USER': '',
        'PASSWORD': '',
    }
}

SECRET_KEY = 'TESTING_TESTING'

