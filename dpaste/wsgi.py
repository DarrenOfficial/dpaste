"""
WSGI config for foobar project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
# If a 'settings_local' file is present, use it
try:
    from dpaste.settings import local
    settings_module = "dpaste.settings.local"
except ImportError:
    settings_module = "dpaste.settings"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

