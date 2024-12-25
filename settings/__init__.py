"""This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings
https://sobolevn.me/2017/04/managing-djangos-settings

To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from os import environ

import django_stubs_ext
from split_settings.tools import include, optional

if environ.get("CI") is not None:
    import os

    environ.setdefault("DOMAIN_NAME", "dash.storagebox.app")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        }
    }
    os.environ["DJANGO_SECRET_KEY"] = "sdfkojfso9idunf9se0ajfksefjse90i"  # noqa: S105
# Monkeypatching Django, so stubs will work for all generics,
# see: https://github.com/typeddjango/django-stubs
django_stubs_ext.monkeypatch()

# Managing environment via `DJANGO_ENV` variable:
environ.setdefault("DJANGO_ENV", "development")
_ENV = environ["DJANGO_ENV"]

_base_settings = (
    "components/common.py",
    # "components/logging.py",
    # "components/api.py",
    # "components/caches.py",
    # "components/security.py",
    # Select the right env:
    f"environments/{_ENV}.py",
    # Optionally override some settings:
    optional("environments/local.py"),
)

# Include settings:
include(*_base_settings)
