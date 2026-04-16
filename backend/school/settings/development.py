"""Development settings — permissive, debug on, console email."""
from .base import *  # noqa: F401,F403
from decouple import config, Csv

DEBUG = True

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0',
    cast=Csv()
)

# Dev CORS — permissive for local Vite
CORS_ALLOW_ALL_ORIGINS = True
