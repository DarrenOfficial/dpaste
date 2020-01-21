"""
Settings for the testsuite runs.
"""
import django

from .base import *  # noqa

SECRET_KEY = "test-key"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
