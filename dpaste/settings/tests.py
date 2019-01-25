"""
Settings for the test suite
"""

from .base import *

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
}
