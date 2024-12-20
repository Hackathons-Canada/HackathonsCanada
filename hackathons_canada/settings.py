"""
Django settings for hackathons_canada project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

from celery.schedules import crontab
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "CHANGEME"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SITE_URL = "https://hackathonscanada.com"
CUR_YEAR = [2025, 2024]
SITE_ID = 1

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    # Add any other allowed hosts here
]
INTERNAL_IPS = ["127.0.0.1"]

AUTH_USER_MODEL = "core.Hacker"
# Application definition

MEDIA_URL = "/media/"
MEDIA_ROOT = "media/"

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_countries",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.discord",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "django_celery_beat",
    # 'allauth.socialaccount.providers.linkedin',
    "core",
    "dischannelsaver",
    "crispy_forms",
    "crispy_bootstrap4",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "FETCH_USERINFO": True,
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
    },
    "github": {
        "SCOPE": [
            "user",
            "repo",
            "read:org",
        ],
    },
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_STORE_TOKENS = True


# still need to figure this out

# # Custom allauth settings
# # Use username or email as the primary identifier
# ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
# ACCOUNT_EMAIL_REQUIRED = True
# # Make email verification mandatory to avoid junk email accounts
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# # Eliminate need to provide username, as it's a very old practice
# ACCOUNT_USERNAME_REQUIRED = False

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "hackathons_canada.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]
WSGI_APPLICATION = "hackathons_canada.wsgi.application"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

assert os.environ.get("POSTGRES_DB"), "POSTGRES_DB is not set in .env"
assert os.environ.get("POSTGRES_USER"), "POSTGRES_USER is not set in .env"
assert os.environ.get("POSTGRES_PASSWORD"), "POSTGRES_PASSWORD is not set in .env"
assert os.environ.get(
    "POSTGRES_HOST"
), "POSTGRES_HOST is not set in .env. You must use a postgres database with PostGIS installed"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER", "user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = "static/"
STATIC_ROOT = "/tmp"

# Styling settings
CRISPY_TEMPLATE_PACK = "bootstrap4"

SIMPLEUI_LOGO = "//hackathonscanada.com/static/assets/favicon.png"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

COUNTRIES_OVERRIDE = {
    "ONL": {"name": "Online", "numeric": 999, "ioc_code": "ONL"},
}
COUNTRIES_FIRST = ["CA", "US"]
# CELERY CONF

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://valkey:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BACKEND", "redis://valkey:6379/1")

LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://valkey:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Logging settings

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "./access.log",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}

# Custom settings

DISCORD_ARCHIVE_AFTER: int = 14  # days
DISCORD_ARCHIVE_ENABLED: bool = True
DISCORD_ARCHIVE_LIMIT: int = (
    10  # max amnt of channels that can be over but not archived
)
DISCORD_ARCHIVE_CATEGORY_ID: int = (
    0  # The discord category ID that you want to archive to
)
DISCORD_ACTIVE_CATEGORY_ID: int = (
    0  # The discord category ID that you want to archive from and create channels to
)
DISCORD_GUILD_ID: int = 0  # The discord guild ID that you want to archive channels from
DISCORD_TOKEN: str = (
    "CHANGEME"  # The discord bot token that you want to use to archive channels
)

DEFAULT_FROM_EMAIL = "hello@hackathonscanada.com"

EMAIL_BATCH_SIZE = 50  # Number of emails to send in a batch

# fmt: off


# Admin settings - https://unfoldadmin.com/
UNFOLD = {
    "SITE_HEADER": _("Hackathons Canada Admin"),
    "SITE_SYMBOL": "dynamic_form",
    "SITE_URL": "/",
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_HISTORY": True,
    "ENVIRONMENT": "hackathons_canada.callbacks.environment_callback",
    # "DASHBOARD_CALLBACK": "hackathons_canada.views.dashboard_callback",
    "SITE_ICON": lambda request: static("assets/logo.png"),
    #
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("favicon.png"),
        },
    ],
    "COLORS": {
        "primary": {
            "50": "200 196 255",
            "100": "194 185 255",
            "200": "186 170 255",
            "300": "172 144 254",
            "400": "153 105 252",
            "500": "134 68 247",
            "600": "117 40 234",
            "700": "100 27 206",
            "800": "85 26 168",
            "900": "70 22 135",
            "950": "47 5 100"
        }
    },
    "LOGIN": {
        "image": lambda request: static("images/login-bg.jpg"), # TODO ADD AN IMG (see https://demo.unfoldadmin.com/admin/login/?next=/admin/)
    },
    # "TABS": [
    #     {
    #         "models": ["core.hacker"],
    #         "items": [
    #             {
    #                 "title": _("Drivers"),
    #                 "icon": "sports_motorsports",
    #                 "link": reverse_lazy("admin:core_hacker_changelist"),
    #             },
    #         ],
    #     },
    # ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "hide_empty_categories": True,
        "navigation": [
            {
                "title": _("Hackathons"),
                "items": [
                    {
                        "title": _("Hackathons"),
                        "icon": "calendar_apps_script",
                        "link": lambda request: reverse_lazy(
                            "admin:core_hackathon_changelist"
                        ),
                        "badge": "core.utils.unreviewed_hackathons",
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:core_category_changelist"),
                    },

                ],
            },
            {
                "title": _("Users & Groups"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Hackers"),
                        "icon": "person",
                        "link": reverse_lazy("admin:core_hacker_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": _("Email Addresses"),
                        "icon": "email",
                        "link": reverse_lazy("admin:account_emailaddress_changelist"),
                    }
                ],
            },
            { #      todo: add celery in admin
                "title": _("Celery Tasks"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Clocked"),
                        "icon": "hourglass_bottom",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_clockedschedule_changelist"
                        ),
                        },
                ],

            },
        ],
    },
}


CELERY_BEAT_SCHEDULE = {
    'weekly-digest': {
        'task': 'hackathons.tasks.send_hackathon_digest',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM UTC
        'kwargs': {'frequency': 'weekly'}
    },
    'monthly-digest': {
        'task': 'hackathons.tasks.send_hackathon_digest',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month 9 AM UTC
        'kwargs': {'frequency': 'monthly'}
    },
}






try:
    with open(os.path.join(os.path.dirname(__file__), "local_settings.py")) as f:
        exec(f.read(), globals())
except IOError:
    raise TypeError(
        "There is an error in the naming of local_settings.py or it doesn't exist. Please read docs for proper setup steps."
    )

# fmt: on

if SECRET_KEY == "CHANGEME" and DEBUG is False:
    raise ValueError("Please set SECRET_KEY in local_settings.py")
