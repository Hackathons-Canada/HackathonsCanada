from settings.components import config

DEBUG = False  # noqa: F405

SECRET_KEY = config("SECRET_KEY", default="")


assert SECRET_KEY != "", "SECRET_KEY is not set to a proper value"
