# ==============================================================================
# Import global settings to make it easier to extend settings.
# ==============================================================================
import os
import sys

import dj_database_url

import dpaste

env = os.environ.get

BASE_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(dpaste.__file__))
)

# ==============================================================================
# Settings
# ==============================================================================

DEBUG = env("DEBUG") == "True"

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = env("SECRET_KEY", "secret-key")

ALLOWED_HOSTS = env("ALLOWED_HOSTS", "*").split(",")

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

LANGUAGE_CODE = "en"
LANGUAGES = (("en", "English"),)

# LOCALE_PATHS = (
#     os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locale')),
# )

STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATIC_ROOT = env("STATIC_ROOT", ".static")
MEDIA_ROOT = env("MEDIA_ROOT", ".media")

STATIC_URL = "/static/"

ROOT_URLCONF = "dpaste.urls"

WSGI_APPLICATION = "dpaste.wsgi.application"

MIDDLEWARE = [
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
            ]
        },
    }
]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "staticinline.apps.StaticInlineAppConfig",
    "dpaste.apps.dpasteAppConfig",
]

sys.stdout.write(f"\n🐘  Database URL is: {env('DATABASE_URL')}\n")
DATABASES = {
    "default": dj_database_url.config(default="sqlite:///dpaste.sqlite")
}

# ==============================================================================
# App specific settings
# ==============================================================================

# If this project installation was built with production settings,
# add that webserver right away.
try:
    import django_webserver  # noqa

    INSTALLED_APPS.append("django_webserver")
    sys.stdout.write(
        f'\n🚀  Production webserver installed. Will run on port {env("PORT")}\n'
    )
except ImportError:
    pass

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        }
    },
}
