from pastebin.conf.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'pastebin.conf.dev.urls'

MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pastebin',
#        'USER': 'dbuser',
#        'PASSWORD': 'dbpassword',
    }
}
