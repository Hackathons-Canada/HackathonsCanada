from settings.components.common import SECRET_KEY, DEBUG

if DEBUG is True:
    raise ValueError("Please set DEBUG to False in production.py")

if SECRET_KEY == "CHANGEME":
    raise ValueError("Please set SECRET_KEY in production.py")
