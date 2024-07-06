"""
Django settings for canadahackers project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "CHANGEME"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    # Add any other allowed hosts here
]

AUTH_USER_MODEL = "core.Hacker"
# Application definition

INSTALLED_APPS = [
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
    # 'allauth.socialaccount.providers.linkedin',
    "core",
    "dischannelsaver",
    'crispy_forms',
]

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

ROOT_URLCONF = "canadahackers.urls"

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
WSGI_APPLICATION = "canadahackers.wsgi.application"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("POSTGRES_DB", os.path.join(BASE_DIR, "db.sqlite3")),
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

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

COUNTRIES_OVERRIDE = {
    "ONL": {"name": "Online", "numeric": 999, "ioc_code": "ONL"},
}
COUNTRIES_FIRST = ["CA", "US"]
### CELERY CONF

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://valkey:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BACKEND", "redis://valkey:6379/1")

LOGIN_REDIRECT_URL = "/"  # todo change to profile page once created

### Custom settings

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

try:
    from .local_settings import *
except ImportError:
    try:
        from local_settings import *
    except ImportError:
        raise ImportError(
            "Please create a local_settings.py with overrides for settings.py"
        )

if SECRET_KEY == "CHANGEME" and DEBUG is False:
    raise ValueError("Please set SECRET_KEY in local_settings.py")
