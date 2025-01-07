"""This file contains all the settings that defines the development src.

SECURITY WARNING: don't run with debug turned on in production!
"""

from settings.components.common import DATABASES

# Setting the development status:

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",  # noqa: S104
    "127.0.0.1",
    "[::1]",
]

INTERNAL_IPS = ["127.0.0.1"]

CORS_ALLOW_ALL_ORIGINS = True


# SILK
# MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
# INSTALLED_APPS.append("silk")
# SILKY_PYTHON_PROFILER = True


# DEBUG TOOLBAR
# INSTALLED_APPS.append("debug_toolbar")
# MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Disable persistent DB connections
# https://docs.djangoproject.com/en/4.2/ref/databases/#caveats
DATABASES["default"]["CONN_MAX_AGE"] = 0

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


STATIC_ROOT = "/static"


# Needed if you want to use the map widgets
# MAP_WIDGETS["GoogleMap"]["apiKey"] = "CHANGE_ME"  # noqa

# If you want to override the default logging location
# LOGGING["handlers"]["file"]["filename"] = "/logs/access.log"  # noqa

DISCORD_GUILD_ID = 1186761885354311780
DISCORD_ARCHIVE_CATEGORY_ID = 1196919673363632178
DISCORD_ACTIVE_CATEGORY_ID = 1186762053180993576
DISCORD_TOKEN = ""
