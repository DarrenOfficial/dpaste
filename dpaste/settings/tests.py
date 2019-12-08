"""
Settings for the testsuite runs.
"""
import django

from .base import *  # noqa

SECRET_KEY = "test-key"

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
}

# Drop CSP middleware for Django 3.0 until it was fixed upstream
# https://github.com/mozilla/django-csp/issues/129
if django.get_version().startswith("3."):
    MIDDLEWARE.remove("csp.middleware.CSPMiddleware")
