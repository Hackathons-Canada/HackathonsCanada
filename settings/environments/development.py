"""This file contains all the settings that defines the development src.

SECURITY WARNING: don't run with debug turned on in production!
"""

from settings.components.common import DATABASES, INSTALLED_APPS, MIDDLEWARE

# Setting the development status:

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",  # noqa: S104
    "127.0.0.1",
    "[::1]",
]
CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
INSTALLED_APPS.append("silk")
SILKY_PYTHON_PROFILER = True

# Disable persistent DB connections
# https://docs.djangoproject.com/en/4.2/ref/databases/#caveats
DATABASES["default"]["CONN_MAX_AGE"] = 0

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


STATIC_ROOT = "/static"
