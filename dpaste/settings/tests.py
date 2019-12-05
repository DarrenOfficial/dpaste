"""
Settings for the test suite
"""

from .base import *

SECRET_KEY = 'test-key'

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
}
