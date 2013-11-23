from dpaste.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Martin Mahner', 'martin@mahner.org'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dpaste',
        'USER': 'root',
        'PASSWORD': '',
    }
}

SECRET_KEY = 'dYWVXop)XYyUT+gqeBpoX]cTDweFJOsNC'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'